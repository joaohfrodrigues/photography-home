import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { getPhotos, getAllCollections } from '@/lib/photos'
import { GalleryClient } from '@/components/photography/gallery-client'

export const metadata: Metadata = {
  title: 'Photography',
  description: 'Street, travel, and portrait photography by João Rodrigues.',
}

export default async function PhotographyPage() {
  const [{ photos, hasMore }, collections] = await Promise.all([
    getPhotos({ page: 1, perPage: 30, sort: 'popular' }),
    getAllCollections(),
  ])

  return (
    <div className="container mx-auto px-4 py-10">
      <header className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2">Photography</h1>
        <p className="text-muted-foreground text-lg">
          {photos.length > 0
            ? `${photos[0]?.photographer.name ?? 'João Rodrigues'} — street, travel, and portrait.`
            : 'Street, travel, and portrait photography.'}
        </p>
      </header>

      {/* Collections row */}
      {collections.length > 0 && (
        <section className="mb-10" aria-label="Collections">
          <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4">
            Collections
          </h2>
          <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1">
            {collections.map((col) => (
              <Link
                key={col.id}
                href={`/photography/${col.slug}`}
                className="group shrink-0 w-44 flex flex-col gap-2"
              >
                <div className="relative h-28 overflow-hidden rounded-md bg-muted">
                  {col.coverPhotoUrl && (
                    <Image
                      src={col.coverPhotoUrl}
                      alt={col.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      sizes="176px"
                    />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium leading-snug group-hover:underline">{col.title}</p>
                  <p className="text-xs text-muted-foreground">{col.totalPhotos} photos</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      <GalleryClient initialPhotos={photos} initialHasMore={hasMore} />
    </div>
  )
}
