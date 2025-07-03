numero_vlan= int(input("Ingresa el número de VLAN."))
if numero_vlan >= 1 and numero_vlan <= 1005:
    print("LA VLAN PERTENECE AL RANGO NORMAL.")
elif numero_vlan >= 1006 and numero_vlan <= 4094:
    print("EL NÚMERO DE VLAN PERTENECE AL RANGO EXTENDIDO.")
else: 
    print ("EL NÚMERO DE VLAN NO ES VÁLIDO.")