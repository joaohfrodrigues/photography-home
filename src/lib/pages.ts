import 'server-only'
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const PAGES_DIR = path.join(process.cwd(), 'content', 'pages')

export interface Page {
  slug: string
  title: string
  description: string
  content: string
}

/**
 * Reads a static markdown page from content/pages/<slug>.md.
 * Returns null if the file doesn't exist, so callers can `notFound()`.
 */
export function getPage(slug: string): Page | null {
  const file = path.join(PAGES_DIR, `${slug}.md`)
  if (!fs.existsSync(file)) return null

  const { data, content } = matter(fs.readFileSync(file, 'utf8'))
  return {
    slug,
    title: (data.title as string) || slug,
    description: (data.description as string) || '',
    content,
  }
}
