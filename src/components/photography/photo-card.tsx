'use client'

import Image from 'next/image'
import type { Photo } from '@/lib/photos'

interface Props {
  photo: Photo
  onClick: () => void
  priority?: boolean
}

export function PhotoCard({ photo, onClick, priority = false }: Props) {
  const alt = photo.altDescription || photo.title || 'Photograph by João Rodrigues'

  return (
    <button
      data-testid="photo-card"
      onClick={onClick}
      className="group relative block w-full overflow-hidden rounded-sm bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label={alt}
    >
      <Image
        src={photo.url}
        alt={alt}
        width={photo.width || 1080}
        height={photo.height || 720}
        sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
        className="w-full h-auto block transition-transform duration-300 group-hover:scale-[1.02]"
        placeholder={photo.blurDataURL ? 'blur' : 'empty'}
        blurDataURL={photo.blurDataURL || undefined}
        priority={priority}
      />

      {/* Unsplash attribution — shown on hover */}
      <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <a
          href={photo.photographer.profileUrl || `https://unsplash.com/@${photo.photographer.username}`}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-xs text-white/90 hover:text-white hover:underline"
        >
          {photo.photographer.name}
        </a>
        {' '}
        <a
          href={photo.unsplashUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-xs text-white/70 hover:text-white/90 hover:underline"
        >
          on Unsplash
        </a>
      </div>
    </button>
  )
}
