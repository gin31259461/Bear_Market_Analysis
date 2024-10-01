# Bear Market Analysis

## 篩選步驟

1. 分成每 8 個月一組，每一組挑高低值各一
2. 連續出現高接高或低接低，無論順序要刪除其中較低（高）值，直到沒有出現連續的高接高或低接低
3. 刪除前後 6 個月的高低值，做第二步驟
4. 以高到低，低到高為一週期，若週期小於 16 個月（包括等於），
   則刪除後面一筆高低值，做第二步驟，直到沒有週期小於 16 個月
5. 刪除週期 < 4 個月的高低值 (除非漲幅 > 20%)

## Usage

1. prepare environment

   ```bash
   python -m venv .venv

   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. run `main.py`

3. result will store in result folder
