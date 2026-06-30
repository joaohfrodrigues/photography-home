import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Music',
  description: 'Gigs and setlists from the band.',
}

export default function MusicPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-24 text-center">
      <h1 className="text-4xl font-bold tracking-tight mb-3">Music</h1>
      <p className="text-muted-foreground text-lg">
        Gigs and setlists from the band — coming soon.
      </p>
    </div>
  )
}
