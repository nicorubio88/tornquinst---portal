#!/usr/bin/env python3
"""Firma un APK (ya alineado con zipalign) con el esquema de firma APK v2 de Android.
Uso: firmar_apk.py entrada.apk salida.apk clave.pem certificado.der
No requiere el SDK de Android. Esquema: https://source.android.com/docs/security/features/apksigning/v2"""
import struct, sys, hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ALG_RSA_PKCS1_SHA256 = 0x0103
V2_ID = 0x7109871A
MAGIC = b'APK Sig Block 42'
CHUNK = 1024 * 1024

def lp(b): return struct.pack('<I', len(b)) + b          # length-prefixed (uint32)

def eocd_offset(d):
    for i in range(len(d) - 22, max(-1, len(d) - 22 - 65536), -1):
        if d[i:i+4] == b'PK\x05\x06': return i
    raise SystemExit('No es un ZIP/APK valido (sin EOCD)')

def digest_secciones(secciones):
    trozos = []
    for s in secciones:
        for i in range(0, len(s), CHUNK):
            c = s[i:i+CHUNK]
            trozos.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(c)) + c).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(trozos)) + b''.join(trozos)).digest()

def firmar(entrada, salida, pem, der):
    d = open(entrada, 'rb').read()
    eo = eocd_offset(d)
    cd_off = struct.unpack('<I', d[eo+16:eo+20])[0]
    cd_size = struct.unpack('<I', d[eo+12:eo+16])[0]
    if d[cd_off-16:cd_off] == MAGIC: raise SystemExit('El APK ya tiene un bloque de firma')
    entradas, central, eocd = d[:cd_off], d[cd_off:cd_off+cd_size], bytearray(d[eo:])
    clave = serialization.load_pem_private_key(open(pem, 'rb').read(), None)
    cert = open(der, 'rb').read()
    pub = clave.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    # el digest se calcula con el EOCD apuntando al inicio del bloque de firma (= offset original del directorio central)
    dig = digest_secciones([entradas, central, bytes(eocd)])
    signed_data = (lp(lp(struct.pack('<I', ALG_RSA_PKCS1_SHA256) + lp(dig)))   # digests
                   + lp(lp(cert))                                               # certificados
                   + lp(b''))                                                   # atributos adicionales
    firma = clave.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    signer = lp(signed_data) + lp(lp(struct.pack('<I', ALG_RSA_PKCS1_SHA256) + lp(firma))) + lp(pub)
    valor = lp(lp(signer))
    par = struct.pack('<Q', 4 + len(valor)) + struct.pack('<I', V2_ID) + valor
    tam = len(par) + 8 + 16                                   # pares + tamaño final + magic
    bloque = struct.pack('<Q', tam) + par + struct.pack('<Q', tam) + MAGIC
    nuevo_cd = cd_off + len(bloque)
    eocd[16:20] = struct.pack('<I', nuevo_cd)
    open(salida, 'wb').write(entradas + bloque + central + bytes(eocd))

if __name__ == '__main__':
    if len(sys.argv) != 5: raise SystemExit(__doc__)
    firmar(*sys.argv[1:])
    print('Firmado:', sys.argv[2])
