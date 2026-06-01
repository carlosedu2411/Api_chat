import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import prisma from './prisma.js';

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({
    status: 'online'
  });
});

// =========================
// BUSCAR USUÁRIO
// =========================

app.get('/buscar_usuario/:nome', async (req, res) => {
  try {

    const usuario = await prisma.user.findFirst({
      where: {
        username: req.params.nome
      }
    });

    if (!usuario) {
      return res.json(null);
    }

    res.json({
      id: usuario.id,
      nome: usuario.username
    });

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// =========================
// ENVIAR MENSAGEM
// =========================

app.post('/enviar', async (req, res) => {
  try {

    const {
      remetente,
      destinatario,
      texto
    } = req.body;

    const mensagem = await prisma.message.create({
      data: {
        mensagem: texto,
        remetenteId: Number(remetente),
        destinatarioId: Number(destinatario)
      }
    });

    res.status(201).json(mensagem);

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// =========================
// CARREGAR MENSAGENS
// =========================

app.get('/mensagens/:id', async (req, res) => {
  try {

    const usuarioAtual = Number(req.query.usuario);
    const contato = Number(req.params.id);

    const mensagens = await prisma.message.findMany({
      where: {
        OR: [
          {
            remetenteId: usuarioAtual,
            destinatarioId: contato
          },
          {
            remetenteId: contato,
            destinatarioId: usuarioAtual
          }
        ]
      },
      orderBy: {
        createdAt: 'asc'
      }
    });

    res.json(
      mensagens.map(m => ({
        remetente: m.remetenteId,
        mensagem: m.mensagem
      }))
    );

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// =========================
// LISTAR CONVERSAS
// =========================

app.get('/conversas/:id', async (req, res) => {
  try {

    const usuarioId = Number(req.params.id);

    const mensagens = await prisma.message.findMany({
      where: {
        OR: [
          { remetenteId: usuarioId },
          { destinatarioId: usuarioId }
        ]
      },
      include: {
        remetente: true,
        destinatario: true
      }
    });

    const contatos = new Map();

    mensagens.forEach(m => {

      const outro =
        m.remetenteId === usuarioId
          ? m.destinatario
          : m.remetente;

      contatos.set(outro.id, {
        id: outro.id,
        nome: outro.username
      });

    });

    res.json([...contatos.values()]);

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});