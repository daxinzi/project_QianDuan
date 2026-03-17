const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(express.json());

// MongoDB 连接
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/writing-space';

mongoose.connect(MONGO_URI)
  .then(() => console.log('MongoDB 连接成功'))
  .catch(err => console.error('MongoDB 连接失败:', err.message));

// 用户模型
const userSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  avatar: { type: String, default: '' },
  role: { type: String, default: 'user' },
  articles: { type: Number, default: 0 },
  status: { type: String, default: 'normal' },
  date: { type: String, default: () => new Date().toISOString().split('T')[0] }
});

const User = mongoose.model('User', userSchema);

// 文章模型
const articleSchema = new mongoose.Schema({
  title: { type: String, default: '' },
  content: { type: String, default: '' },
  authorId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  author: { type: String, default: '' },
  category: { type: String, default: '' },
  status: { type: String, default: 'draft' },
  views: { type: Number, default: 0 },
  likes: { type: Number, default: 0 },
  date: { type: String, default: () => new Date().toISOString().split('T')[0] },
  chapters: [{
    name: String,
    content: String
  }]
});

const Article = mongoose.model('Article', articleSchema);

// API 路由

// 用户相关
app.post('/api/users/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: '该邮箱已被注册' });
    }

    const user = new User({
      username,
      email,
      password,
      avatar: username.charAt(0).toUpperCase(),
      role: 'user',
      articles: 0,
      status: 'normal'
    });

    await user.save();
    res.json({ 
      message: '注册成功',
      user: { id: user._id, username: user.username, email: user.email, role: user.role }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/users/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const user = await User.findOne({ email, password });
    if (!user) {
      return res.status(401).json({ error: '邮箱或密码错误' });
    }

    if (user.status === 'disabled') {
      return res.status(403).json({ error: '账号已被禁用' });
    }

    res.json({ 
      message: '登录成功',
      user: { id: user._id, username: user.username, email: user.email, role: user.role }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/users', async (req, res) => {
  try {
    const users = await User.find().sort({ _id: -1 });
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put('/api/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { username, email, password, status } = req.body;
    
    const updateData = { username, email, status };
    if (password) updateData.password = password;

    const user = await User.findByIdAndUpdate(id, updateData, { new: true });
    res.json({ message: '更新成功', user });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/users/:id', async (req, res) => {
  try {
    await User.findByIdAndDelete(req.params.id);
    res.json({ message: '删除成功' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 文章相关
app.get('/api/articles', async (req, res) => {
  try {
    const articles = await Article.find().sort({ _id: -1 });
    res.json(articles);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/articles', async (req, res) => {
  try {
    const { title, content, authorId, author, category, status, chapters } = req.body;
    
    const article = new Article({
      title,
      content,
      authorId,
      author,
      category,
      status,
      chapters: chapters || []
    });

    await article.save();
    
    // 更新用户文章数
    if (authorId && status === 'published') {
      await User.findByIdAndUpdate(authorId, { $inc: { articles: 1 } });
    }

    res.json({ message: '保存成功', article });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/articles/:id', async (req, res) => {
  try {
    const article = await Article.findById(req.params.id);
    res.json(article);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put('/api/articles/:id', async (req, res) => {
  try {
    const article = await Article.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json({ message: '更新成功', article });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/articles/:id', async (req, res) => {
  try {
    await Article.findByIdAndDelete(req.params.id);
    res.json({ message: '删除成功' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 统计接口
app.get('/api/stats', async (req, res) => {
  try {
    const userCount = await User.countDocuments();
    const articleCount = await Article.countDocuments();
    res.json({ userCount, articleCount });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
});
