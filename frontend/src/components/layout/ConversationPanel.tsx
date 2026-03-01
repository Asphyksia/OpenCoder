"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { useAppStore, type Conversation } from "@/store/useAppStore"
import { 
  Plus, Search, X, Trash2, 
  MessageSquare, Pin, PinOff, FolderOpen
} from "lucide-react"
import { StatusBadge } from "@/components/common/StatusBadge"

export function ConversationPanel() {
  const { 
    panelOpen, 
    setPanelOpen,
    conversations,
    activeConversationId,
    createConversation,
    loadConversation,
    deleteConversation,
    agentStatus,
    selectedModel,
    repoPath,
    messages,
    saveCurrentConversation,
  } = useAppStore()
  
  const [searchQuery, setSearchQuery] = useState("")
  
  // Save current conversation when messages change
  useEffect(() => {
    if (messages.length > 0 && activeConversationId) {
      const timeout = setTimeout(() => {
        saveCurrentConversation()
      }, 1000)
      return () => clearTimeout(timeout)
    }
  }, [messages, activeConversationId, saveCurrentConversation])
  
  // Filter conversations
  const filteredConversations = searchQuery
    ? conversations.filter(c => 
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : conversations
  
  // Group by date
  const grouped = groupByDate(filteredConversations)
  
  if (!panelOpen) return null
  
  return (
    <>
      {/* Overlay for mobile */}
      <div 
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={() => setPanelOpen(false)}
      />
      
      {/* Panel */}
      <aside className={cn(
        "fixed lg:static inset-y-0 left-0 z-50 w-[280px] h-full",
        "bg-card border-r border-border flex flex-col",
        "transform transition-transform duration-300",
        panelOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-border">
          <h2 className="font-semibold">Conversaciones</h2>
          <button 
            onClick={() => setPanelOpen(false)}
            className="p-2 hover:bg-muted rounded-md lg:hidden"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        {/* New conversation button */}
        <div className="p-3">
          <button
            onClick={() => {
              createConversation()
              setPanelOpen(false)
            }}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg
                       bg-primary text-primary-foreground hover:bg-primary/90
                       transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            Nueva conversación
          </button>
        </div>
        
        {/* Search */}
        <div className="px-3 pb-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm bg-muted rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>
        
        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto px-2">
          {Object.entries(grouped).map(([group, convs]) => (
            convs.length > 0 && (
              <div key={group} className="mb-4">
                <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase">
                  {group}
                </div>
                <div className="space-y-1">
                  {convs.map(conv => (
                    <ConversationItem
                      key={conv.id}
                      conversation={conv}
                      isActive={conv.id === activeConversationId}
                      onSelect={() => {
                        loadConversation(conv.id)
                        setPanelOpen(false)
                      }}
                      onDelete={() => deleteConversation(conv.id)}
                    />
                  ))}
                </div>
              </div>
            )
          ))}
          
          {filteredConversations.length === 0 && (
            <div className="text-center text-muted-foreground py-8 text-sm">
              {searchQuery ? 'Sin resultados' : 'Sin conversaciones'}
            </div>
          )}
        </div>
        
        {/* Footer - Status */}
        <div className="border-t border-border p-3 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Estado</span>
            <StatusBadge status={agentStatus} />
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Modelo</span>
            <span className="text-xs font-mono truncate max-w-[140px]">
              {selectedModel?.split('/').pop() || 'Qwen3'}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Repositorio</span>
            <span className="text-xs font-mono truncate max-w-[140px]">
              {repoPath}
            </span>
          </div>
        </div>
      </aside>
    </>
  )
}

// Conversation item component
function ConversationItem({ 
  conversation, 
  isActive, 
  onSelect, 
  onDelete 
}: { 
  conversation: Conversation
  isActive: boolean
  onSelect: () => void
  onDelete: () => void
}) {
  const [showMenu, setShowMenu] = useState(false)
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return 'Ahora'
    if (minutes < 60) return `${minutes}m`
    if (hours < 24) return `${hours}h`
    if (days < 7) return `${days}d`
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }
  
  return (
    <div
      onClick={onSelect}
      className={cn(
        "group flex items-start gap-2 p-2 rounded-lg cursor-pointer",
        "hover:bg-muted transition-colors",
        isActive && "bg-muted"
      )}
    >
      <MessageSquare className="w-4 h-4 mt-0.5 text-muted-foreground flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">
          {conversation.title}
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-2">
          <span>{conversation.messages.length} msgs</span>
          <span>•</span>
          <span>{formatDate(conversation.updatedAt)}</span>
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onDelete()
        }}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/20 rounded transition-opacity"
        title="Eliminar"
      >
        <Trash2 className="w-3 h-3 text-destructive" />
      </button>
    </div>
  )
}

// Group conversations by date
function groupByDate(conversations: Conversation[]) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86400000)
  const weekAgo = new Date(today.getTime() - 7 * 86400000)
  
  return {
    'Recientes': conversations.filter(c => new Date(c.updatedAt) >= weekAgo),
    'Anteriores': conversations.filter(c => new Date(c.updatedAt) < weekAgo),
  }
}
