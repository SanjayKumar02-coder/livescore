import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const API = "http://127.0.0.1:5000";
const EVENT_ID = 1;

export default function App() {
  const [board, setBoard] = useState([]);
  const [live, setLive] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user") || "null"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pid, setPid] = useState("");
  const [points, setPoints] = useState("");
  const [pname, setPname] = useState("");
  const [college, setCollege] = useState("");
  const [msg, setMsg] = useState("");

  const loadBoard = () =>
    fetch(`${API}/api/events/${EVENT_ID}/leaderboard`).then((r) => r.json()).then(setBoard);

  useEffect(() => {
    loadBoard();
    const socket = io(API);
    socket.on("connect", () => {
      setLive(true);
      socket.emit("join_event", { event_id: EVENT_ID });
    });
    socket.on("disconnect", () => setLive(false));
    socket.on("leaderboard_update", setBoard);
    return () => socket.disconnect();
  }, []);

  const post = (path, body) =>
    fetch(API + path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(body),
    }).then((r) => r.json());

  const login = async () => {
    const res = await post("/api/auth/login", { email, password });
    if (res.token) {
      localStorage.setItem("token", res.token);
      localStorage.setItem("user", JSON.stringify(res.user));
      setToken(res.token);
      setUser(res.user);
      setMsg("");
    } else setMsg(res.error || "Login failed");
  };

  const logout = () => {
    localStorage.clear();
    setToken(null);
    setUser(null);
  };

  const addScore = async () => {
    const res = await post(`/api/events/${EVENT_ID}/scores`, {
      participant_id: Number(pid),
      points: Number(points),
    });
    setMsg(res.error || "Score added ✅");
    setPoints("");
  };

  const addParticipant = async () => {
    const res = await post(`/api/events/${EVENT_ID}/participants`, { name: pname, college });
    setMsg(res.error || "Participant added ✅");
    setPname("");
    setCollege("");
    loadBoard();
  };

  const input = "w-full bg-slate-700 rounded-lg px-3 py-2 outline-none";
  const btn = "bg-amber-500 text-slate-900 font-semibold rounded-lg px-4 py-2";
  const isStaff = user && ["organizer", "admin"].includes(user.role);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Live Scoreboard</h1>
          <span className={live ? "text-green-400" : "text-red-400"}>
            ● {live ? "LIVE" : "Offline"}
          </span>
        </div>

        <div className="space-y-2">
          {board.map((p) => (
            <div key={p.participant_id} className="flex items-center justify-between bg-slate-800 rounded-xl px-4 py-3">
              <div className="flex items-center gap-4">
                <span className="text-xl font-bold w-8">#{p.rank}</span>
                <div>
                  <div className="font-semibold">{p.name}</div>
                  <div className="text-sm text-slate-400">{p.college}</div>
                </div>
              </div>
              <span className="text-2xl font-bold text-amber-400">{p.total}</span>
            </div>
          ))}
          {board.length === 0 && <p className="text-slate-400">No participants yet.</p>}
        </div>

        <div className="bg-slate-800 rounded-xl p-4 space-y-3">
          {!user ? (
            <>
              <h2 className="font-semibold">Organizer Login</h2>
              <input className={input} placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <input className={input} type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <button className={btn} onClick={login}>Login</button>
            </>
          ) : (
            <>
              <div className="flex justify-between">
                <span>{user.name} ({user.role})</span>
                <button className="text-slate-400 underline" onClick={logout}>Logout</button>
              </div>
              {isStaff && (
                <>
                  <h2 className="font-semibold pt-2">Add Score</h2>
                  <select className={input} value={pid} onChange={(e) => setPid(e.target.value)}>
                    <option value="">Select participant</option>
                    {board.map((p) => (
                      <option key={p.participant_id} value={p.participant_id}>{p.name}</option>
                    ))}
                  </select>
                  <input className={input} type="number" placeholder="Points" value={points} onChange={(e) => setPoints(e.target.value)} />
                  <button className={btn} onClick={addScore}>Add Score</button>

                  <h2 className="font-semibold pt-2">Add Participant</h2>
                  <input className={input} placeholder="Name" value={pname} onChange={(e) => setPname(e.target.value)} />
                  <input className={input} placeholder="College" value={college} onChange={(e) => setCollege(e.target.value)} />
                  <button className={btn} onClick={addParticipant}>Add Participant</button>
                </>
              )}
            </>
          )}
          {msg && <p className="text-sm text-slate-300">{msg}</p>}
        </div>
      </div>
    </div>
  );
}