import json
import os
import random
import re

STATE_PATH = "game_state.json"
README_PATH = "README.md"
START_MARKER = "<!-- TICTACTOE:START -->"
END_MARKER = "<!-- TICTACTOE:END -->"

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

def fresh_state():
    return {"board": [""] * 9, "status": "in_progress"}

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return fresh_state()

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None

def bot_move(board):
    empties = [i for i, v in enumerate(board) if not v]
    for i in empties:
        trial = board[:]
        trial[i] = "O"
        if winner(trial) == "O":
            return i
    for i in empties:
        trial = board[:]
        trial[i] = "X"
        if winner(trial) == "X":
            return i
    for i in [4, 0, 2, 6, 8, 1, 3, 5, 7]:
        if i in empties:
            return i
    return random.choice(empties)

def parse_move(title):
    match = re.search(r"move\s*:\s*([0-8])", title or "", re.IGNORECASE)
    return int(match.group(1)) if match else None

def render_board(board, status, repo):
    cells = []
    for i, v in enumerate(board):
        if status == "in_progress" and v:
            cells.append(f'<td align="center" width="46">{v}</td>')
        else:
            url = f"https://github.com/{repo}/issues/new?title=move%3A{i}"
            label = v if v else "&#183;"
            cells.append(f'<td align="center" width="46"><a href="{url}">{label}</a></td>')
    rows = [cells[0:3], cells[3:6], cells[6:9]]
    table = ['<table align="center">']
    for row in rows:
        table.append("<tr>" + "".join(row) + "</tr>")
    table.append("</table>")
    if status == "human_wins":
        caption = "You won! Opening a new move starts a fresh game."
    elif status == "bot_wins":
        caption = "The bot won this round. Opening a new move starts a fresh game."
    elif status == "draw":
        caption = "Draw. Opening a new move starts a fresh game."
    else:
        caption = "Click an open square to play as X."
    return "\n".join(table) + f'\n\n<p align="center"><sub>{caption}</sub></p>'

def update_readme(board_html):
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1:
        raise SystemExit("TICTACTOE markers not found in README.md")
    new_content = (
        content[: start + len(START_MARKER)]
        + "\n\n" + board_html + "\n\n"
        + content[end:]
    )
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    title = os.environ.get("ISSUE_TITLE", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "your-username/your-username")
    state = load_state()

    if state["status"] != "in_progress":
        state = fresh_state()

    move = parse_move(title)
    if move is not None and not state["board"][move]:
        state["board"][move] = "X"
        result = winner(state["board"])
        if result:
            state["status"] = "human_wins" if result == "X" else "draw"
        else:
            b = bot_move(state["board"])
            state["board"][b] = "O"
            result = winner(state["board"])
            if result:
                state["status"] = "bot_wins" if result == "O" else "draw"

    save_state(state)
    update_readme(render_board(state["board"], state["status"], repo))

if __name__ == "__main__":
    main()
