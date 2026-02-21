# 📺 YouTube Daily Upload Tracker

Private dashboard that checks 5 Tamil finance YouTube channels for today's uploads with a single button click.

---

## 🗂 Project Structure

```
yt-dashboard/
├── app.py               ← Flask routes (2 routes only)
├── youtube_checker.py   ← All YouTube API logic
├── templates/
│   └── index.html       ← Dashboard UI
├── static/
│   ├── style.css        ← Dark theme styles
│   └── script.js        ← Frontend fetch + render
├── .env                 ← Your API key (never commit this)
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

**1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**2 — Add your API key**

Open `.env` and replace the placeholder:
```
YOUTUBE_API_KEY=your_actual_key_here
```

**3 — Run**
```bash
python app.py
```

**4 — Open browser**
```
http://127.0.0.1:5000
```

Click **"Check Updates"** — done.

---

## 🔐 Security

- The API key is stored in `.env` and loaded only by Python
- It is **never sent to the browser** or included in any JS
- The frontend only calls `/check` — it receives clean JSON, nothing else
- Add `.env` to your `.gitignore` if you push this to GitHub:
  ```
  .env
  __pycache__/
  *.pyc
  ```

---

## 📊 How it works

1. User clicks "Check Updates" in browser
2. Browser calls `GET /check`
3. Flask calls `youtube_checker.check_all_channels()`
4. For each of 5 channels: YouTube Search API is called with `publishedAfter = today 00:00 IST`
5. Results (JSON) returned to browser
6. JavaScript renders channel cards dynamically

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `YOUTUBE_API_KEY is not set` | Open `.env`, paste your real key |
| `API quota exceeded` | Wait until midnight UTC (quota resets daily) |
| No videos showing | Channels may not have uploaded yet today |
| Port already in use | Change `PORT=5001` in `.env` |
