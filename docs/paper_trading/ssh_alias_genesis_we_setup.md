# SSH Alias Setup for `genesis-we` (Home Computer)

Purpose: configure a stable SSH alias used by Genesis remote orchestration from your home computer.

Applies to:

- Local workstation (Windows/Linux/macOS)
- Remote target used by `scripts/run/phase3_remote_orchestrate.ps1`

Related:

- `docs/paper_trading/phase3_runbook.md`
- `docs/paper_trading/operations_summary.md`
- `docs/paper_trading/server_setup.md`
- `scripts/run/phase3_remote_orchestrate.ps1`

---

## Prerequisites

- VM host or DNS name
- SSH username
- Private key file path
- OpenSSH client installed locally

Recommended security baseline:

- Key-based SSH only (no password auth)
- Restricted SSH ingress (trusted source IP only)
- Verify host fingerprint before trust

---

## Alias contract

Alias name must be exactly:

- `genesis-we`

Expected behavior:

- `ssh genesis-we` opens a VM shell
- Remote orchestration can use alias without explicit `user@host`
- You can still override target via `GENESIS_SSH_TARGET`

---

## Windows setup (PowerShell + OpenSSH)

### 1) Ensure SSH directory exists

Run:

`mkdir $HOME\.ssh -Force`

### 2) Add alias block to `$HOME\.ssh\config`

Use this template:

```sshconfig
Host genesis-we
    HostName <VM_HOST_OR_IP>
    User <SSH_USER>
    IdentityFile <FULL_PATH_TO_PRIVATE_KEY>
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

### 3) Restrict private key access

Ensure your key file is readable only by your user account.

### 4) First connection

Run:

`ssh genesis-we`

Confirm host fingerprint before accepting.

---

## Linux/macOS setup

### 1) Ensure secure SSH directory/file permissions

Run:

`mkdir -p ~/.ssh && chmod 700 ~/.ssh`

`touch ~/.ssh/config && chmod 600 ~/.ssh/config`

### 2) Add alias block to `~/.ssh/config`

Use this template:

```sshconfig
Host genesis-we
    HostName <VM_HOST_OR_IP>
    User <SSH_USER>
    IdentityFile ~/.ssh/<PRIVATE_KEY_FILE>
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

### 3) Restrict key file permissions

Run:

`chmod 600 ~/.ssh/<PRIVATE_KEY_FILE>`

### 4) First connection

Run:

`ssh genesis-we`

Confirm host fingerprint before accepting.

---

## Verification

### Basic SSH check

Run:

`ssh genesis-we "whoami && hostname && pwd"`

Expected:

- command executes successfully
- output shows VM user and host

### Genesis orchestration compatibility check

From repo root, run a dry-run:

`pwsh ./scripts/run/phase3_remote_orchestrate.ps1 -DryRun`

Expected:

- alias resolves correctly
- no placeholder target errors
- script reports selected SSH target

---

## Troubleshooting

### Could not resolve host `genesis-we`

- Check `~/.ssh/config` / `%USERPROFILE%\.ssh\config`
- Ensure `Host genesis-we` block exists and has no indentation mistakes

### Permission denied (publickey)

- Verify `IdentityFile` path
- Verify key permissions (`600` on Unix-like systems)
- Confirm VM has corresponding public key in `~/.ssh/authorized_keys`

### Host key mismatch

If VM was recreated/rotated, clean stale entries and reconnect:

`ssh-keygen -R genesis-we`

`ssh-keygen -R <VM_HOST_OR_IP>`

---

## Rollback

1. Backup your SSH config.
2. Remove the `Host genesis-we` block.
3. Test direct connection with explicit `ssh <user>@<host>`.
4. Unset/remove `GENESIS_SSH_TARGET` override if previously set.

---

## Security notes

- Never commit private keys, local SSH config secrets, or tokens.
- Do not commit local secret files such as:
  - `.env`
  - `dev.overrides.local.json`
  - `.nonce_tracker.json`
- Prefer least-privilege access and explicit host validation.
