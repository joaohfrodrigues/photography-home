import { PhotoCard } from './photo-card'
import type { Photo } from '@/lib/photos'

interface Props {
  photos: Photo[]
  onPhotoClick: (index: number) => void
}

export function PhotoGrid({ photos, onPhotoClick }: Props) {
  if (photos.length === 0) {
    return (
      <p className="text-center text-muted-foreground py-12">No photos found.</p>
    )
  }

  return (
    <div className="columns-2 sm:columns-3 lg:columns-4 gap-2">
      {photos.map((photo, i) => (
        <div key={photo.id} className="break-inside-avoid mb-2">
          <PhotoCard
            photo={photo}
            onClick={() => onPhotoClick(i)}
            priority={i < 8}
          />
        </div>
      ))}
    </div>
  )
}
