import { NextRequest, NextResponse } from 'next/server'
import { getPhotos, searchPhotos } from '@/lib/photos'
import type { SortOrder } from '@/lib/photos'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const query = searchParams.get('q') || ''
  const sort = (searchParams.get('sort') || 'popular') as SortOrder
  const page = Math.max(1, parseInt(searchParams.get('page') || '1', 10))
  const perPage = Math.min(60, Math.max(1, parseInt(searchParams.get('perPage') || '30', 10)))
  const collectionId = searchParams.get('collectionId') || ''

  const result =
    query || collectionId
      ? searchPhotos({ query, page, perPage, sort, collectionId: collectionId || undefined })
      : getPhotos({ page, perPage, sort })

  return NextResponse.json(result)
}
