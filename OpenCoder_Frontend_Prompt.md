# PROMPT DE INICIO DEL FRONTEND - OpenCoder

## Rol y Objetivo

Actúa como un **Senior Frontend Architect** y **UI/UX Specialist** con experiencia en Next.js 15, React 19, y diseño de interfaces para herramientas de desarrollo/IA. Tu misión es diseñar y codificar el frontend de **OpenCoder**, una herramienta de "Agentic Coding" que permite a usuarios interactuar con un agente de IA para editar código.

El backend (FastAPI + Aider + OpenGPU Relay) ya está completo y funcional. Este frontend debe consumir esa API REST y proporcionar una experiencia de usuario moderna, intuitiva y profesional.

---

## Tech Stack

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Next.js** | 15.x (App Router) | Framework principal |
| **React** | 19.x | UI Components |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Styling |
| **shadcn/ui** | Latest | Component library |
| **Zustand** | Latest | State management |
| **React Query** | Latest | Server state & caching |
| **Framer Motion** | Latest | Animations |
| **Lucide Icons** | Latest | Iconography |
| **Socket.io-client** | Latest | Real-time updates (opcional) |

---

## API Backend Disponible

### Endpoints REST

```
GET  /                    # Info de la API
GET  /health              # Health check
GET  /models              # Lista de modelos disponibles
GET  /pricing             # Información de precios
GET  /status              # Estado del repositorio y sesión
POST /chat                # Enviar mensaje al agente
DELETE /session/{id}      # Cerrar sesión
```

### Schemas de Datos

**ChatRequest:**
```json
{
  "message": "string (required)",
  "model": "string (optional, default: gpt-4o)",
  "read_only": "boolean (optional, default: false)"
}
```

**ChatResponse:**
```json
{
  "success": "boolean",
  "message": "string",
  "events": [
    {
      "event_type": "thinking | planning | editing | error | system | git | file",
      "content": "string",
      "timestamp": "string"
    }
  ],
  "file_changes": [
    {
      "filename": "string",
      "diff": "string",
      "operation": "created | modified | deleted"
    }
  ],
  "diffs": "string (combined diffs)",
  "error": "string | null"
}
```

**StatusResponse:**
```json
{
  "status": "ready | no_session | busy | error",
  "repo_path": "string",
  "read_only": "boolean",
  "events_count": "number",
  "file_changes_count": "number",
  "available_models": ["string"],
  "error": "string | null"
}
```

**ModelsResponse:**
```json
{
  "models": [
    {
      "name": "provider/model-name",
      "provider": "string",
      "type": "text-to-text",
      "category": "auto | direct | opengpu"
    }
  ],
  "count": "number"
}
```

---

## Filosofía de Diseño

### Principios Core

1. **Clean & Minimal**: La interfaz debe ser limpia, con mucho espacio en blanco. Evitar el clutter visual.
2. **Progressive Disclosure**: Mostrar información básica por defecto, con opción de expandir para ver detalles.
3. **Status Visibility**: El usuario siempre debe saber qué está haciendo el agente sin sentirse abrumado.
4. **Professional Aesthetic**: Aspecto de herramienta profesional de desarrollo, no de chatbot genérico.
5. **Dark Mode First**: Diseñar principalmente para dark mode con opción de light mode.

### Inspiración de Diseño

- **Cursor IDE**: Chat lateral limpio, diffs integrados
- **Vercel AI SDK**: Estilo de chat moderno con thinking blocks
- **Linear**: Minimalismo, animaciones sutiles, status indicators
- **GitHub Copilot**: Integración no intrusiva en el flujo de trabajo

---

## Arquitectura de Componentes

### Estructura de Carpetas Propuesta

```
src/
├── app/
│   ├── layout.tsx          # Root layout con providers
│   ├── page.tsx            # Main page (dashboard/chat)
│   └── globals.css         # Tailwind + custom styles
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/
│   │   ├── Sidebar.tsx     # Navegación lateral (opcional)
│   │   ├── Header.tsx      # Header con status y controles
│   │   └── Footer.tsx      # Footer con info
│   ├── chat/
│   │   ├── ChatContainer.tsx    # Contenedor principal del chat
│   │   ├── MessageList.tsx      # Lista de mensajes
│   │   ├── MessageItem.tsx      # Mensaje individual (user/assistant)
│   │   ├── MessageInput.tsx     # Input para escribir mensajes
│   │   └── EventStream.tsx      # Visualización de eventos en tiempo real
│   ├── agent/
│   │   ├── AgentStatus.tsx      # Indicador de estado del agente
│   │   ├── AgentEvents.tsx      # Lista de eventos del agente
│   │   ├── FileChanges.tsx      # Lista de archivos modificados
│   │   └── DiffViewer.tsx       # Visualizador de diffs
│   ├── models/
│   │   ├── ModelSelector.tsx    # Dropdown para seleccionar modelo
│   │   ├── ModelCard.tsx        # Card con info del modelo
│   │   └── PricingInfo.tsx      # Información de precios
│   └── common/
│       ├── StatusBadge.tsx      # Badge de estado (ready, busy, error)
│       ├── LoadingDots.tsx      # Animación de carga
│       ├── CodeBlock.tsx        # Bloque de código con syntax highlighting
│       └── Collapsible.tsx      # Panel colapsable reutilizable
├── hooks/
│   ├── useChat.ts           # Hook para lógica de chat
│   ├── useStatus.ts         # Hook para status del agente
│   ├── useModels.ts         # Hook para lista de modelos
│   └── useStreaming.ts      # Hook para respuestas streaming
├── lib/
│   ├── api.ts               # Cliente API (fetch wrappers)
│   ├── types.ts             # TypeScript interfaces
│   └── utils.ts             # Utilidades generales
├── store/
│   └── useAppStore.ts       # Zustand store global
└── styles/
    └── animations.ts        # Framer Motion variants
```

---

## Componentes Clave - Especificaciones

### 1. Header Component
```
┌──────────────────────────────────────────────────────────────────┐
│ 🟢 OpenCoder          [Model: gpt-4o ▾]    [Settings] [Theme]   │
│    Agent Ready                                                      │
└──────────────────────────────────────────────────────────────────┘
```
- Logo/Nombre a la izquierda
- Status badge con indicador de color (green=ready, yellow=busy, red=error)
- Model selector dropdown
- Controles de settings y theme a la derecha

### 2. Main Chat Area
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  👤 User                                                          │
│  Create a Python function that calculates fibonacci               │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  🤖 OpenCoder · gpt-4o · 2.3s                                     │
│  ├─ 💭 Thinking...                                                │
│  │   Analyzing the request for fibonacci function...              │
│  │                                                                │
│  ├─ 📝 Planning                                                   │
│  │   I'll create a recursive fibonacci implementation             │
│  │                                                                │
│  ├─ ✏️ Editing                                                    │
│  │   Created file: fibonacci.py                                   │
│  │   ──────────────────────────────────                           │
│  │   + def fibonacci(n):                                          │
│  │   +     if n <= 1: return n                                    │
│  │   +     return fibonacci(n-1) + fibonacci(n-2)                 │
│  │   ──────────────────────────────────                           │
│  │                                                                │
│  └─ ✅ Complete                                                   │
│      Created fibonacci.py with recursive implementation            │
│                                                                   │
│  [View Diff] [View Files]                                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 3. Message Input
```
┌──────────────────────────────────────────────────────────────────┐
│ ┌────────────────────────────────────────────────────────────┐   │
│ │ Type your message or command...                            │ ▾ │
│ └────────────────────────────────────────────────────────────┘   │
│ [📎 Attach] [🎯 ReadOnly] [Model: gpt-4o ▾]         [Send →]     │
└──────────────────────────────────────────────────────────────────┘
```
- Textarea expandable
- Botón de attach (para futuras funcionalidades)
- Toggle de read-only mode
- Selector de modelo rápido
- Botón de send con icono

### 4. Status Sidebar (Colapsable)
```
┌─────────────────────┐
│ 📊 Session Status   │
├─────────────────────┤
│ Status: ● Ready     │
│ Model: gpt-4o       │
│ Repo: ./workspace   │
│ Events: 12          │
│ Changes: 3 files    │
├─────────────────────┤
│ 📁 Modified Files   │
│ ├─ fibonacci.py     │
│ ├─ utils.py         │
│ └─ main.py          │
├─────────────────────┤
│ 🔧 Available Models │
│ ├─ openai/gpt-4o    │
│ ├─ openai/gpt-4     │
│ ├─ anthropic/claude │
│ └─ ollama/llama3    │
└─────────────────────┘
```

### 5. Event Stream Visualization
Los eventos deben mostrar iconos diferentes según el tipo:
- `thinking` → 💭 (icono cerebro, color gris)
- `planning` → 📋 (icono clipboard, color azul)
- `editing` → ✏️ (icono lápiz, color verde)
- `file` → 📄 (icono archivo, color azul claro)
- `git` → 🔀 (icono git, color naranja)
- `error` → ❌ (icono X, color rojo)
- `system` → ⚙️ (icono gear, color gris)
- `complete` → ✅ (icono check, color verde)

---

## Estados de UI

### Agent Status States

| Estado | Color | Descripción |
|--------|-------|-------------|
| `ready` | 🟢 Green | Agente listo para recibir mensajes |
| `busy` | 🟡 Yellow | Agente procesando mensaje |
| `error` | 🔴 Red | Error en el agente |
| `no_session` | ⚪ Gray | Sin sesión activa |

### Message States

| Estado | Visual |
|--------|--------|
| Sending | Spinner + "Sending..." |
| Processing | Progress indicator con eventos en tiempo real |
| Success | Checkmark + "Complete" |
| Error | Error icon + mensaje de error |

---

## Responsive Design

### Breakpoints

- **Mobile** (< 640px): Chat full-width, sidebar como drawer
- **Tablet** (640px - 1024px): Chat con sidebar colapsable
- **Desktop** (> 1024px): Layout completo con sidebar visible

### Mobile Considerations
- Input siempre visible en la parte inferior
- Sidebar como drawer lateral
- Eventos colapsados por defecto
- Diffs en modal/pantalla separada

---

## Funcionalidades Específicas

### 1. Real-time Event Streaming
Los eventos del agente deben aparecer en tiempo real mientras se procesa:
```
💭 Thinking...           (aparece primero)
   Analyzing code...
📝 Planning              (aparece después)
   Creating new file...
✏️ Editing               (aparece mientras edita)
   + def new_function():
```
Usar animaciones sutiles para la aparición de cada evento.

### 2. Diff Visualization
Los diffs deben mostrarse con syntax highlighting:
- Líneas añadidas: fondo verde claro
- Líneas eliminadas: fondo rojo claro
- Números de línea a la izquierda
- Opción de copiar diff

### 3. Model Selection
El selector de modelos debe:
- Mostrar modelos agrupados por provider
- Indicar disponibilidad (some models pueden estar offline)
- Mostrar pricing estimate si está disponible
- Permitir búsqueda/filtrado

### 4. Session Persistence
- Historial de mensajes en la sesión actual
- Opción de limpiar historial
- Opción de exportar conversación

---

## Instrucciones de Ejecución

Por favor, sigue estos pasos para iniciar el frontend:

### Fase 1: Setup Inicial
1. Crear proyecto Next.js 15 con App Router
2. Configurar Tailwind CSS 4.x
3. Instalar y configurar shadcn/ui
4. Configurar theme dark/light mode
5. Crear estructura de carpetas

### Fase 2: Core Components
1. Implementar tipos TypeScript (`lib/types.ts`)
2. Crear cliente API (`lib/api.ts`)
3. Implementar Zustand store (`store/useAppStore.ts`)
4. Crear hooks base (`useChat`, `useStatus`, `useModels`)

### Fase 3: UI Components
1. Layout components (Header, Sidebar, Footer)
2. Chat components (ChatContainer, MessageList, MessageInput)
3. Agent components (AgentStatus, EventStream, DiffViewer)
4. Common components (StatusBadge, CodeBlock, Collapsible)

### Fase 4: Integration
1. Conectar con el backend (http://localhost:8000)
2. Implementar flujo de chat completo
3. Manejar estados de loading y error
4. Implementar persistencia de sesión

### Fase 5: Polish
1. Añadir animaciones con Framer Motion
2. Implementar keyboard shortcuts
3. Optimizar para accesibilidad
4. Tests de integración básicos

---

## Restricciones y Estilo

- **TypeScript estricto**: Todo debe estar tipado, evitar `any`
- **Componentes funcionales**: Usar hooks, no class components
- **Server Components**: Usar donde sea apropiado para SEO/performance
- **Client Components**: Solo donde sea necesario (`'use client'`)
- **Accesibilidad**: WCAG 2.1 Level AA compliance
- **Performance**: Lighthouse score > 90
- **Código limpio**: Funciones pequeñas, componentes reutilizables

---

## Notas Adicionales

### Variables de Entorno
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=OpenCoder
```

### Configuración de API
El frontend debe manejar:
- Timeouts de requests (default: 120s para chat)
- Retry logic para errores de red
- Cancelación de requests en curso
- Manejo de CORS

### Futuras Funcionalidades (No implementar ahora)
- WebSocket para streaming real-time
- Multiple sessions/tabs
- File upload para contexto
- Voice input
- Export/import de conversaciones
- Plugins/extensions system

---

## Entregables Esperados

1. **Proyecto Next.js completo** con la estructura descrita
2. **Todos los componentes** funcionando e integrados
3. **Conexión con el backend** operativa
4. **README.md** con instrucciones de setup y uso
5. **Screenshots o demo** de la interfaz funcionando

---

Empieza mostrándome la estructura de archivos que vas a crear y luego procede a generar el código de los componentes clave, comenzando por los tipos, el store, y los componentes de layout.
