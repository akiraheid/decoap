# Decoap specification

## Introduction
Decoap manages the download and configuration of desktop container applications (decoaps) so that decoaps can run as if they were native desktop application while still providing the benefits of using containers.

This document specifies how images must be built in order for Decoap to properly support the decoap.

## Specification

The following subsections detail the requirements a decoap must follow in order to be supported by Decoap.

### Application launcher

An application launcher is an entry in the host system that allows ...

### Desktop icon

Decoaps MAY have icons that will be displayed as the application icon on the desktop. If a decoap has icons, the icons MUST be stored in the following directory in the image:

```text
/decoap/icons/
```

Icon files must be named `icon[-[size]].[ext]`.

These icons are renamed and copied to the directory that stores application icons for the host system. On Linux-based systems, icons are generally installed to `~/.local/share/icons`

#### Recommendations

* Linux-based systems generally prefer an `ext` of `png`.
* `size` can be omitted, but 32x32 is generally acceptable for icon size.

#### Examples

An icon.

```
/decoap/icons/icon.png
```

A 32x32 icon.

```
/decoap/icons/icon-32.png
```

### 
