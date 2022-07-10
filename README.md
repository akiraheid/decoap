The desktop container application manager.

Decoap manages the download and configuration of desktop container applications (decoaps) so that decoaps can run as if they were native desktop application while still providing the benefits of using containers.

# Usage

Run the script and name the image to install.

```bash
python3 decoap.py docker.io/example/image
```

The application will then be installed and accessible via the application menu.

# Make a decoap-compliant image

In the Dockerfile, add the following files to `/decoap/`:
* `manifest.json`
* `icons/icon.png`

## Formatting manifest.json

The manifest determines default runtime settings and desktop integration.

### Manifest options

Required fields
| Name      | Type | Description |
| `appName` | String | Application name. Used as the desktop integration name. |
| `containerName` | String | Name of the container. Used to pull the container from a registry E.g. `docker.io/_/alpine` |

Optional fields
| Name | Type | Default | Description |
| `devices` | Array | `[]` | The host devices to attach to the container. |
| `detach` | Boolean | `true` | Run as a detached application. |
| `env` | Array | `[]` | Array of environment variables and values. E.g. `["VARIABLE=value", "VARIABLE2=value2"]`. |
| `mimeTypes` | Array | `[]` | [MIME types](https://en.wikipedia.org/wiki/Media_type) this application can open. E.g. `["audio/mp3", "video/mp4"]`. |
| `rm` | Boolean | `true` | Delete the container after exiting. |
| `singleton` | Boolean | `false` | Only allow one instance of the application at a time. |
| `userns` | String | `keep-id` | User namespace to use for the container. |
| `volumes` | Array | `[]` | Strings defining container volume mounts. |

## Application icons

Application icons are displayed in the application menu.
Although optional, it is recommended to have an icon with the application so that it is easier to identify visually.

Icons are stored in `/decoap/icons/` in the image and icon files must be named `icon[-[size]].[ext]`.
For example, `/decoap/icons/icon.png` or `/decoap/icons/icon-64.jpg`.
`size` can be omitted, but 32x32 is generally acceptable for icon size.

Linux-based systems generally prefer an `ext` of `png`.
