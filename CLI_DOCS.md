# `gitmopy`

**Usage**:

```console
$ gitmopy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `commit`: Commit staged files.
* `config`: Configure gitmopy
* `info`: Print gitmopy info

## `gitmopy commit`

Commit staged files. Use --add to interactively select files to stage if none is already staged

**Usage**:

```console
$ gitmopy commit [OPTIONS]
```

**Options**:

* `--repo TEXT`: Path to the git repository  [default: .]
* `--add / --no-add`: Whether or not to interactively select files to stage if none is already staged  [default: no-add]
* `--push / --no-push`: Whether to `git push` after commit. If multiple remotes exist, you will be asked to interactively choose the ones to push to. Use --remote to skip interactive selection. Disabled by default.
* `--dry / --no-dry`: Whether or not to actually commit.  [default: no-dry]
* `--remote TEXT`: Remote to push to after commit. Use to skip interactive remote selection when several exist. Use several '--remote {remote name}' to push to multiple remotes
* `--keep-alive / --no-keep-alive`: Whether or not to keep the app alive after commit, to be ready for another one.   [default: no-keep-alive]
* `--help`: Show this message and exit.

## `gitmopy config`

Configure gitmopy

**Usage**:

```console
$ gitmopy config [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `gitmopy info`

Print gitmopy info

**Usage**:

```console
$ gitmopy info [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
