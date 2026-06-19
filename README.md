# Uncle Ossy StoryTeller

A Streamlit-first personal writing assistant for poems, spoken word, short stories, novels, and non-fiction projects.

## Features in this first build

- Local login and local JSON storage
- Project dashboard
- Project creation wizard
- OpenRouter default provider with Gemini fallback
- Separate model settings for writing, outline, editing, research, continuity, QA, marketing, and export
- Full outline generation
- Chapter-by-chapter workflow with approval gate
- Rewrite chapter in a different tone
- Editable Story Bible: characters, locations, plot points, timeline, themes, world rules, objects, relationships, unresolved threads, glossary, chapter summaries
- Automatic chapter summary and Story Bible update prompt
- Contradiction warning prompt
- Custom style profile creation
- Export to Markdown, HTML, DOCX, PDF, and EPUB
- Back-cover blurb and book cover prompt generation
- KOP blue theme with modern writing studio UI

## Quick start on Windows

1. Open `.env.local` and add your API keys.
2. Double-click `start.bat`.
3. Visit the local URL shown in the terminal.
4. Login with the username and password in `.env.local`.

Default login:

```text
admin / change-me
```

Change it before serious use.

## Manual start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 8443
```

## Storage

Projects are saved under:

```text
data/projects/<project_slug>/
```

Each project has:

- `project.json`
- `outline.json`
- `story_bible.json`
- `chapters.json`
- `continuity_log.json`
- `qa_reports.json`
- `custom_style.json`
- `exports/`

## Future roadmap

- Supabase Auth and Postgres
- Vercel frontend
- React Native mobile app
- Shared Supabase backend for Streamlit, Vercel, and mobile
- Team/collaboration mode
- Cover image generation
