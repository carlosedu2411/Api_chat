import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import prisma from './prisma.js';

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Home
app.get('/', (req, res) => {
  res.json({
    status: 'online',
    service: 'chat-api'
  });
});

// Buscar mensagens
app.get('/messages', async (req, res) => {
  try {
    const messages = await prisma.message.findMany({
      orderBy: {
        createdAt: 'asc'
      }
    });

    res.json(messages);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Criar mensagem
app.post('/messages', async (req, res) => {
  try {
    const { userId, username, content } = req.body;

    if (!userId || !username || !content) {
      return res.status(400).json({
        error: 'Dados obrigatórios ausentes'
      });
    }

    const message = await prisma.message.create({
      data: {
        userId,
        username,
        content
      }
    });

    res.status(201).json(message);

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Deletar mensagem
app.delete('/messages/:id', async (req, res) => {
  try {
    await prisma.message.delete({
      where: {
        id: Number(req.params.id)
      }
    });

    res.json({
      message: 'Mensagem removida'
    });

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});