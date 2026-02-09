import 'dart:async';
import 'package:flutter/material.dart';
import 'package:olympics_preparation_client/services/socket_service.dart';
import 'package:timer_widget/timer_widget.dart';

class DuelPage extends StatefulWidget {
  final String duelName;
  final String username;
  final int userRating;
  final String opponent;
  final int opponentRating;

  const DuelPage({
    super.key,
    required this.duelName,
    required this.username,
    required this.userRating,
    required this.opponent,
    required this.opponentRating,
  });

  @override
  State<DuelPage> createState() => DuelPageState();
}

enum DuelStatus { waitingForStart, playing, roundResult, finished }

class DuelPageState extends State<DuelPage> {
  final socketService = SocketService();
  final TextEditingController controller = TextEditingController();

  // Game State
  DuelStatus status = DuelStatus.waitingForStart;
  String currentTask = "";
  int roundDuration = 0;
  String roundId = "init"; 

  // Logic Timer (The fix)
  Timer? _logicTimer;
  bool _hasAnswered = false;

  // Scores
  num userScore = 0;
  num opponentScore = 0;

  // Round Result Data
  bool? lastAnswerCorrect;
  num? lastRoundPoints;
  String? correctAnswer;

  @override
  void initState() {
    super.initState();
    socketService.duelNotifier.addListener(_onSocketEvent);
    
    socketService.sendMessage(widget.duelName, {
      "operation": "join",
      "username": widget.username,
    });
  }

  @override
  void dispose() {
    _logicTimer?.cancel(); // Always cancel timers!
    socketService.duelNotifier.removeListener(_onSocketEvent);
    controller.dispose();
    super.dispose();
  }

  void _onSocketEvent() {
    final data = socketService.duelNotifier.value;
    if (data == null) return;

    // Use addPostFrameCallback to avoid "setState during build" errors
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      
      setState(() {
        if (data["code"] == "new_round") {
          status = DuelStatus.playing;
          currentTask = data["task"];
          roundDuration = data["duration"];
          roundId = DateTime.now().toIso8601String();
          controller.clear();
          
          lastAnswerCorrect = null;
          lastRoundPoints = null;
          _hasAnswered = false;

          // --- THE FIX: Start a logic timer to force end the round ---
          _logicTimer?.cancel();
          _logicTimer = Timer(Duration(seconds: roundDuration), _handleTimeout);
        } 
        else if (data["code"] == "answerResponse") {
          final score = data["score"] as num;
          final isCorrect = data["isCorrect"] as bool;
          final toUser = data["toUser"];

          if (toUser == widget.username) {
            userScore += score;
            status = DuelStatus.roundResult;
            lastAnswerCorrect = isCorrect;
            lastRoundPoints = score;
            correctAnswer = data["correctAnswer"];
            _hasAnswered = true;
            _logicTimer?.cancel(); // Stop timer since we answered
          } else {
            opponentScore += score;
          }
        } 
        else if (data["code"] == "end_game") {
          _logicTimer?.cancel();
          status = DuelStatus.finished;
        }
      });
    });
  }

  // Called automatically when timer hits 0
  void _handleTimeout() {
    if (_hasAnswered || !mounted) return;
    print("Time is up! Auto-submitting.");
    _submitAnswer(isTimeout: true);
  }

  void _submitAnswer({bool isTimeout = false}) {
    if (_hasAnswered) return;
    
    // If it's a timeout, we send an empty string.
    // If it's a manual submit, we check if text is empty.
    if (!isTimeout && controller.text.trim().isEmpty) return;

    _hasAnswered = true;
    _logicTimer?.cancel(); // Stop the timer
    
    socketService.sendMessage(widget.duelName, {
      "username": widget.username,
      "operation": "answer",
      "answer": isTimeout ? "" : controller.text.trim(),
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Дуэль"),
        centerTitle: true,
        automaticallyImplyLeading: false, 
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            _buildScoreBoard(),
            const SizedBox(height: 20),
            Expanded(child: _buildGameArea()),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreBoard() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 8.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildPlayerInfo(widget.username, widget.userRating, userScore, true),
            _buildTimer(),
            _buildPlayerInfo(widget.opponent, widget.opponentRating, opponentScore, false),
          ],
        ),
      ),
    );
  }

  Widget _buildPlayerInfo(String name, int rating, num score, bool isUser) {
    return Column(
      children: [
        Text(
          name,
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        Text(
          "$rating elo",
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        Text(
          "$score",
          style: TextStyle(
            fontSize: 24, 
            fontWeight: FontWeight.bold,
            color: isUser ? Colors.blue : Colors.red,
          ),
        ),
      ],
    );
  }

  Widget _buildTimer() {
    if (status == DuelStatus.waitingForStart || status == DuelStatus.finished) {
      return Icon(Icons.timer_off, color: Colors.grey);
    }
    
    // We use the Widget only for visuals. 
    // The logic is handled by _logicTimer in the State.
    return TimerWidget(
      key: Key(roundId), 
      id: "timer_$roundId",
      autoStart: true,
      timerType: TimerType.countdown,
      timeOutInSeconds: roundDuration,
      builder: (context, state) {
        return Column(
          children: [
            Icon(Icons.timer, color: state.remainingSeconds < 10 ? Colors.red : Colors.black),
            Text(
              "${state.remainingSeconds}s",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        );
      },
    );
  }

  Widget _buildGameArea() {
    switch (status) {
      case DuelStatus.waitingForStart:
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: const [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text("Ожидание начала дуэли...", style: TextStyle(fontSize: 18)),
            ],
          ),
        );

      case DuelStatus.playing:
        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text("Задание", style: TextStyle(fontSize: 14, color: Colors.grey[700])),
                      const SizedBox(height: 8),
                      Text(
                        currentTask,
                        style: TextStyle(fontSize: 18),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 30),
              TextField(
                controller: controller,
                decoration: InputDecoration(
                  labelText: "Ваш ответ",
                  border: OutlineInputBorder(),
                  filled: true,
                ),
                textInputAction: TextInputAction.done,
                onSubmitted: (_) => _submitAnswer(),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => _submitAnswer(),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                ),
                child: Text("Ответить", style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        );

      case DuelStatus.roundResult:
        final bool correct = lastAnswerCorrect ?? false;
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                correct ? Icons.check_circle : Icons.cancel,
                color: correct ? Colors.green : Colors.red,
                size: 80,
              ),
              const SizedBox(height: 16),
              Text(
                correct ? "Верно!" : "Неверно!",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              if (correct)
                 Text("+$lastRoundPoints очков", style: TextStyle(fontSize: 18))
              else
                 Column(
                   children: [
                     Text("0 очков", style: TextStyle(fontSize: 18)),
                     if (correctAnswer != null)
                        Text("Правильный ответ: $correctAnswer", style: TextStyle(color: Colors.grey)),
                   ],
                 ),
              const SizedBox(height: 30),
              LinearProgressIndicator(),
              const SizedBox(height: 8),
              Text("Ожидание соперника...", style: TextStyle(color: Colors.grey)),
            ],
          ),
        );

      case DuelStatus.finished:
        String resultMessage;
        Color resultColor;
        if (userScore > opponentScore) {
          resultMessage = "Победа!";
          resultColor = Colors.green;
        } else if (userScore < opponentScore) {
          resultMessage = "Поражение";
          resultColor = Colors.red;
        } else {
          resultMessage = "Ничья";
          resultColor = Colors.orange;
        }

        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(resultMessage, style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: resultColor)),
              const SizedBox(height: 20),
              Text("Итоговый счет:", style: TextStyle(fontSize: 20)),
              Text("$userScore : $opponentScore", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              const SizedBox(height: 40),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(), 
                child: Text("Выйти"),
              ),
            ],
          ),
        );
    }
  }
}