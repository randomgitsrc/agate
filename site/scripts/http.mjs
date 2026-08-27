// site/scripts/http.mjs
// 共用 HTTP 封装：用 curl（自动继承 HTTPS_PROXY/HTTP_PROXY env）。
// 为什么不用 Node 全局 fetch：undici 默认不读代理环境变量，本机 127.0.0.1:10808 下会
// UND_ERR_CONNECT_TIMEOUT。curl 原生遵守代理，且 dev.to 实测需浏览器 UA 的场景 curl 已跑通。
import { execFileSync } from 'node:child_process'

const MARK = '__HTTPSTATUS__'

// method: 'GET' | 'POST' | 'PATCH' | 'HEAD'
// 返回 { status: number, text: string }；连接失败抛异常。
export function http(method, url, { headers = {}, body = null } = {}) {
  const args = ['-s', '-S', '-L', '--max-time', '90', '-X', method, '-w', `\n${MARK}%{http_code}`, url]
  for (const [k, v] of Object.entries(headers)) args.push('-H', `${k}: ${v}`)
  if (body != null) args.push('-H', 'Content-Type: application/json', '--data-binary', body)
  let out = ''
  try {
    out = execFileSync('curl', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 })
  } catch (e) {
    // curl 连接层失败（exit != 0）：stdout 仍有部分内容，status 取 e.status
    out = e.stdout || ''
    if (e.code === 'ENOENT') throw new Error('未找到 curl')
    const m = out.match(new RegExp(`${MARK}(\\d{3})\\s*$`))
    const status = m ? +m[1] : -1
    return { status, text: out.replace(new RegExp(`${MARK}\\d{3}\\s*$`), '') }
  }
  const m = out.match(new RegExp(`${MARK}(\\d{3})\\s*$`))
  const status = m ? +m[1] : -1
  const text = out.replace(new RegExp(`${MARK}\\d{3}\\s*$`), '').replace(/\n$/, '')
  return { status, text }
}

export { http as default }
