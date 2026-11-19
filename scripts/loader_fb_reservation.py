"""Preserve a live framebuffer reservation without colliding with LK's node add."""
import struct


def preserve(blob):
    if len(blob)<40:raise ValueError('Truncated FDT')
    magic,total,start,strings,reserve,version,compat,cpu,string_bytes,structure_bytes=struct.unpack_from('>10I',blob)
    if (magic!=0xd00dfeed or total!=len(blob) or version!=17 or compat>17 or
            start<40 or start+structure_bytes>total or strings+string_bytes>total):
        raise ValueError('Bounded version17 FDT required')
    at=start;end=start+structure_bytes;stack=[];matches=[];finished=False
    while at+4<=end:
        token=struct.unpack_from('>I',blob,at)[0];at+=4
        if token==1:
            stop=blob.find(b'\0',at,end)
            if stop<0:raise ValueError('Unterminated FDT node')
            name=blob[at:stop].decode('ascii');parent='/'+('/'.join(stack[1:]))
            if parent=='/reserved-memory' and name.split('@')[0]=='fb-reserved-memory':matches.append((at,stop,name))
            stack.append(name);at=(stop+4)&~3
        elif token==2:
            if not stack:raise ValueError('Unbalanced FDT node')
            stack.pop()
        elif token==3:
            if not stack or at+8>end:raise ValueError('Truncated FDT property')
            length,name=struct.unpack_from('>II',blob,at);at=(at+8+length+3)&~3
            if at>end or name>=string_bytes:raise ValueError('FDT property outside bounds')
        elif token==4:pass
        elif token==9:
            if stack:raise ValueError('Unbalanced FDT end')
            finished=True;break
        else:raise ValueError('Unknown FDT token')
    if not finished or len(matches)!=1:raise ValueError('One live loader framebuffer node required')
    at,stop,name=matches[0];new='fw'+name[2:]
    result=bytearray(blob);result[at:stop]=new.encode()
    if len(result)!=len(blob) or sum(a!=b for a,b in zip(blob,result))!=1:
        raise ValueError('Only one framebuffer node-name byte may change')
    return bytes(result),{'old_path':'/reserved-memory/'+name,'new_path':'/reserved-memory/'+new,
                         'changed_bytes':1,'reservation_properties_unchanged':True,
                         'fdt_reserve_map_unchanged':True}
