import { useState, useEffect } from 'react'
import '../styles/Resizer.css'

interface ResizerProps {
  orientation: 'vertical' | 'horizontal'
  onResize: (delta: number) => void
}

export default function Resizer({ orientation, onResize }: ResizerProps) {
  const [isResizing, setIsResizing] = useState(false)
  const [startPos, setStartPos] = useState(0)

  useEffect(() => {
    if (!isResizing) return

    const handleMouseMove = (e: MouseEvent) => {
      const delta = orientation === 'vertical'
        ? e.clientX - startPos
        : e.clientY - startPos

      onResize(delta)
      setStartPos(orientation === 'vertical' ? e.clientX : e.clientY)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing, startPos, orientation, onResize])

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true)
    setStartPos(orientation === 'vertical' ? e.clientX : e.clientY)
    document.body.style.cursor = orientation === 'vertical' ? 'ew-resize' : 'ns-resize'
    document.body.style.userSelect = 'none'
  }

  return (
    <div
      className={`resizer resizer-${orientation} ${isResizing ? 'resizing' : ''}`}
      onMouseDown={handleMouseDown}
    >
      <div className="resizer-handle" />
    </div>
  )
}
