# 60-Second Demo Recording Script

**Goal**: produce a short screen-capture video of the WorkFlow Arena demo that a judge can watch in under a minute. Embed the resulting GIF/MP4 in README.md so async judges see the environment working without installing anything.

**Target length**: 60-75 seconds.

---

## Before you start

1. **Open the live HF Space** in a fresh browser window (no extensions bar, clean tabs):
   https://huggingface.co/spaces/jaydeepshah2025/workflow-arena
2. **Close dev tools**, **hide bookmarks bar** (`Cmd+Shift+B` on Mac, `Ctrl+Shift+B` on Windows), zoom the page to ~110% so text is readable in the video.
3. Have the page scrolled to the top so the title is visible.
4. **Use a screen recorder**:
   - Mac: `Cmd + Shift + 5` -> Record Selected Portion
   - Windows: Xbox Game Bar (`Win + G`) or OBS
5. Record the browser window only — not the whole screen.

---

## The script (read each line out loud OR put as on-screen caption)

### 0:00-0:10 — Opening (what judges see first)
> *"WorkFlow Arena is a multi-app enterprise RL environment. Every reward is verified by actual API responses — no LLM judges."*

**On screen**: show the top of the Gradio page with title + tagline + the "How to try it" instructions clearly visible. Slowly scroll 1/3 down so judges see the dropdown and buttons.

### 0:10-0:20 — Reset
**On screen**: select `employee_onboarding` from dropdown, click **Reset**.

> *"Five workflows range from easy onboarding to expert P0 incident response. We'll start with employee onboarding."*

**Pause 1 sec** on the initial state — show `Score: 0.00`, `Required Actions: 0/6`.

### 0:20-0:35 — Sample + Execute
**On screen**: click **Sample API Calls**. JSON fills the box — 2 calls: gmail.create_account and hris.create_employee. Hover the cursor briefly over the "reasoning" field in the JSON.

> *"The agent submits API calls as JSON — app, method, params, and reasoning. Here's a correct onboarding step."*

**On screen**: click **Execute Step**.

**Pause 2 sec** for the right panel to update.

### 0:35-0:50 — Point at the proof
**On screen**: slowly move cursor to highlight these four fields, one at a time:
- `Score: 0.33` (go from 0 -> 0.33)
- `Required Actions: 2/6` (counter moved)
- `API Success Rate: 2/2` (both calls actually hit the mock apps)
- `Step 1: 0.333` in the reward history panel

> *"Two required actions completed, both API calls succeeded, and the reward is 0.333 — exactly 1/3 of the max. The grader is deterministic: this isn't an LLM opinion, it's API state."*

### 0:50-1:00 — Switch workflows for variety
**On screen**: change dropdown to `incident_response`. Click **Reset**. Click **Sample API Calls**. Click **Execute Step**.

> *"And it scales — here's the expert-level P0 incident response workflow with the same graded API calls."*

**Pause on the final state** with counters visible.

### 1:00-1:10 — Close with the proof
**On screen**: scroll down OR open GitHub README in a new tab OR cut to the committed reward_curve.png file.

> *"80-episode bandit training against this environment produces clean learning curves — committed directly to the repo."*

**Show the reward_curve.png briefly**.

### 1:10 — End card
> *"WorkFlow Arena. Theme 3.1 plus Scaler AI Labs sub-theme. Link in the description."*

---

## Post-production

1. Trim to 60-75 seconds max.
2. Export as:
   - **MP4** at 1080p for the HF Space description / YouTube
   - **GIF** at 720p, <20 MB, for embedding in the README
3. Upload the GIF to the repo as `demo.gif`. Embed in README under the "Try it in 30 seconds" section:
   ```markdown
   ![WorkFlow Arena Demo](demo.gif)
   ```
4. Optionally upload the MP4 to YouTube (unlisted) and paste the link in the submission form.

---

## What NOT to do in the recording

- Do not narrate hackathon anxiety ("we built this in 2 weeks")
- Do not show the terminal or server logs
- Do not try to complete a full workflow (you'll hit "already exists" errors)
- Do not zoom in/out during the recording
- Do not record with background music — captions or voiceover only

---

## Expected effort

- Setup: 5 minutes
- 2-3 takes until clean: 10 minutes
- Trim + export: 5 minutes
- Total: ~20 minutes

The video is the single highest-leverage async asset you can ship in the remaining time.
