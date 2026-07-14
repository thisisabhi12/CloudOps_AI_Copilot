/**
 * Simple TCP proxy: forwards Windows localhost:8000 → WSL2 Docker backend.
 *
 * WSL2 uses NAT networking, so ports exposed by Docker inside WSL are not
 * always reachable from Windows at 127.0.0.1. This tiny proxy bridges the gap
 * without requiring admin privileges (unlike netsh portproxy).
 *
 * Usage:  node proxy.mjs
 * Stop:   Ctrl+C
 */

import { createServer, createConnection } from "net";
import { execSync } from "child_process";

// Dynamically resolve the WSL2 VM IP (it can change on reboot)
function getWslIp() {
  const raw = execSync('wsl -d Ubuntu -e hostname -I', { encoding: 'utf8' });
  const ip = raw.trim().split(/\s+/)[0];
  if (!ip) throw new Error("Could not resolve WSL2 IP");
  return ip;
}

const WSL_IP = getWslIp();
const LISTEN_PORT = 8000;
const TARGET_PORT = 8000;

console.log(`🔀 Proxying localhost:${LISTEN_PORT} → ${WSL_IP}:${TARGET_PORT}`);

const server = createServer((clientSocket) => {
  const targetSocket = createConnection(TARGET_PORT, WSL_IP, () => {
    clientSocket.pipe(targetSocket);
    targetSocket.pipe(clientSocket);
  });

  targetSocket.on("error", (err) => {
    console.error(`  ✗ Target error: ${err.message}`);
    clientSocket.destroy();
  });

  clientSocket.on("error", (err) => {
    console.error(`  ✗ Client error: ${err.message}`);
    targetSocket.destroy();
  });
});

server.listen(LISTEN_PORT, "127.0.0.1", () => {
  console.log(`✅ Listening on http://127.0.0.1:${LISTEN_PORT}`);
});
