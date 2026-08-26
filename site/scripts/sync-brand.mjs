// 把品牌权威源 docs/brand/ 的所需文件拷贝到 site/public/（构建快照）。
// docs/brand 是唯一权威源；site/public 是生成的快照，已被 .gitignore 忽略。
// 改品牌只在 docs/brand 改，然后 `npm run sync:brand` 同步。
import { cpSync, mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '../..')
const brandDir = resolve(repoRoot, 'docs/brand')
const publicDir = resolve(here, '../public')

mkdirSync(publicDir, { recursive: true })

const files = [
  'logo-mark.svg',
  'logo-mark-dark-bg.svg',
  'logo-lockup.svg',
  'logo-lockup-dark-bg.svg',
  'social-preview.png',
]

for (const f of files) {
  cpSync(resolve(brandDir, f), resolve(publicDir, f))
}

console.log(`synced ${files.length} brand assets → site/public`)
