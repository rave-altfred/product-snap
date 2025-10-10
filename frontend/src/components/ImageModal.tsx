import { useEffect, useState } from 'react'
import { X, ChevronLeft, ChevronRight } from 'lucide-react'

interface ImageModalProps {
  images: string[]
  currentIndex: number
  onClose: () => void
  onNavigate: (index: number) => void
}

export default function ImageModal({ images, currentIndex, onClose, onNavigate }: ImageModalProps) {
  const [imageKey, setImageKey] = useState(0)
  const [imageDimensions, setImageDimensions] = useState<{width: number, height: number} | null>(null)

  // Force image reload when index changes
  useEffect(() => {
    setImageKey(prev => prev + 1)
    setImageDimensions(null)
  }, [currentIndex])

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget
    setImageDimensions({ width: img.naturalWidth, height: img.naturalHeight })
    console.log('Image loaded:', {
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      displayWidth: img.width,
      displayHeight: img.height,
      url: images[currentIndex]
    })
  }

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft' && currentIndex > 0) onNavigate(currentIndex - 1)
      if (e.key === 'ArrowRight' && currentIndex < images.length - 1) onNavigate(currentIndex + 1)
    }

    document.addEventListener('keydown', handleEscape)
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [currentIndex, images.length, onClose, onNavigate])

  return (
    <div 
      className="fixed inset-0 z-50 bg-black bg-opacity-95"
      onClick={onClose}
      style={{
        display: 'grid',
        placeItems: 'center',
        padding: '2rem'
      }}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors z-10"
        title="Close (Esc)"
      >
        <X size={28} />
      </button>

      {/* Navigation buttons */}
      {images.length > 1 && (
        <>
          {currentIndex > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onNavigate(currentIndex - 1)
              }}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 p-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors z-10"
              title="Previous (←)"
            >
              <ChevronLeft size={40} />
            </button>
          )}

          {currentIndex < images.length - 1 && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onNavigate(currentIndex + 1)
              }}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 p-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors z-10"
              title="Next (→)"
            >
              <ChevronRight size={40} />
            </button>
          )}
        </>
      )}

      {/* Image counter */}
      {images.length > 1 && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 text-white bg-black bg-opacity-70 px-4 py-2 rounded-full text-base font-medium z-10">
          {currentIndex + 1} / {images.length}
        </div>
      )}

      {/* Image dimensions debug */}
      {imageDimensions && (
        <div className="absolute top-16 left-1/2 transform -translate-x-1/2 text-white bg-black bg-opacity-70 px-3 py-1 rounded text-sm z-10">
          Natural: {imageDimensions.width}x{imageDimensions.height}
        </div>
      )}

      {/* Image at native resolution */}
      <img
        key={`modal-full-${imageKey}-${currentIndex}`}
        src={images[currentIndex]}
        alt={`Image ${currentIndex + 1}`}
        className="cursor-pointer"
        style={{ 
          maxWidth: '100%',
          maxHeight: '100%',
          objectFit: 'scale-down',
          imageRendering: 'auto'
        }}
        onLoad={handleImageLoad}
        onClick={(e) => e.stopPropagation()}
      />
    </div>
  )
}
