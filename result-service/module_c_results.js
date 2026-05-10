const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// База данных результатов (в памяти)
const resultsDb = {};

// Middleware для логирования
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// POST /results/save — сохранить результат
app.post('/results/save', (req, res) => {
    const { testId, userId, score, maxScore, percentage, passed, completedAt, details } = req.body;
    
    const resultId = Date.now();
    const result = {
        id: resultId,
        testId,
        userId,
        score,
        maxScore,
        percentage,
        passed,
        completedAt,
        details
    };
    
    if (!resultsDb[userId]) {
        resultsDb[userId] = [];
    }
    resultsDb[userId].push(result);
    
    res.json({ 
        success: true, 
        message: "Результат сохранён",
        resultId: resultId
    });
});

// GET /results/:userId — получить историю результатов
app.get('/results/:userId', (req, res) => {
    const userId = parseInt(req.params.userId);
    const userResults = resultsDb[userId] || [];
    
    res.json({
        userId: userId,
        results: userResults,
        totalAttempts: userResults.length
    });
});

// GET /analytics/test/:testId — аналитика по тесту
app.get('/analytics/test/:testId', (req, res) => {
    const testId = parseInt(req.params.testId);
    
    // Собрать все результаты по этому тесту
    let allScores = [];
    for (const userId in resultsDb) {
        const userResults = resultsDb[userId];
        for (const result of userResults) {
            if (result.testId === testId) {
                allScores.push(result.score);
            }
        }
    }
    
    if (allScores.length === 0) {
        return res.json({
            testId: testId,
            averageScore: 0,
            averagePercentage: 0,
            passRate: 0,
            attemptsCount: 0,
            scoreDistribution: {}
        });
    }
    
    const averageScore = allScores.reduce((a, b) => a + b, 0) / allScores.length;
    const passedCount = allScores.filter(score => score >= 60).length;
    const passRate = (passedCount / allScores.length) * 100;
    
    // Распределение баллов (гистограмма)
    const distribution = {
        "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0
    };
    allScores.forEach(score => {
        if (score <= 20) distribution["0-20"]++;
        else if (score <= 40) distribution["21-40"]++;
        else if (score <= 60) distribution["41-60"]++;
        else if (score <= 80) distribution["61-80"]++;
        else distribution["81-100"]++;
    });
    
    res.json({
        testId: testId,
        averageScore: Math.round(averageScore),
        averagePercentage: Math.round(averageScore),
        passRate: Math.round(passRate),
        attemptsCount: allScores.length,
        scoreDistribution: distribution
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`✅ Сервис результатов запущен на http://localhost:${PORT}`);
});