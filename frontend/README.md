# OpenCoder Frontend

Next.js 15 frontend for OpenCoder - an AI-powered coding assistant.

## Prerequisites

- Node.js 18+
- npm or yarn

## Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Create environment file (already created as `.env.local`):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME=OpenCoder
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI**: React 19, Tailwind CSS 4.x
- **State**: Zustand, React Query
- **Icons**: Lucide React
- **Animations**: Framer Motion

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Main page
│   │   └── globals.css   # Global styles
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   ├── layout/       # Header, Sidebar
│   │   ├── chat/         # Chat components
│   │   ├── agent/        # Agent components
│   │   └── common/       # Reusable components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities & API client
│   └── store/            # Zustand store
├── package.json
└── tsconfig.json
```

## Features

- Real-time chat with AI agent
- Live event streaming (thinking, planning, editing)
- Diff viewer for code changes
- Model selection
- Dark/light theme
- Session persistence
- Responsive design

## API Integration

The frontend connects to the backend at `http://localhost:8000` by default. Available endpoints:

- `GET /health` - Health check
- `GET /models` - Available models
- `GET /status` - Agent status
- `POST /chat` - Send message
- `DELETE /session/{id}` - Close session

## Building for Production

```bash
npm run build
npm start
```
