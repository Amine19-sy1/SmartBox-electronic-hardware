import cadquery as cq

# 📐 Paramètres (modifiables)
thickness = 3  # Épaisseur (Z)
hook_length = 30
hook_height = 15
hook_base = 5

lock_length = 15
lock_height = 20
lock_base = 3

# 🪝 Hook (Crochet)
hook = (
    cq.Workplane("XY")
    .moveTo(0, 0)
    .lineTo(hook_length, 0)
    .lineTo(hook_length, 5)
    .lineTo(hook_length - 5, 10)
    .lineTo(10, 10)
    .lineTo(10, hook_height)
    .lineTo(0, hook_height)
    .close()
    .extrude(thickness)
)

# 🔩 Trous de fixation (hook)
hook = hook.faces(">Z").workplane().pushPoints([(5, 3), (5, 12)]).hole(3)

# 🔐 Lock (Verrou à fixer sur porte)
lock = (
    cq.Workplane("XY")
    .moveTo(35, 5)
    .lineTo(35 + lock_length, 5)
    .lineTo(35 + lock_length, 25)
    .lineTo(35, 25)
    .lineTo(35, 20)
    .lineTo(45, 20)
    .lineTo(45, 15)
    .lineTo(35, 15)
    .close()
    .extrude(thickness)
)

# 🔩 Trous de fixation (lock)
lock = lock.faces(">Z").workplane().pushPoints([(47.5, 7), (47.5, 22.5)]).hole(3)

# 🧱 Combinaison des deux pièces (ou tu peux les laisser séparées si tu veux)
assembly = hook.union(lock)

# 💾 Exporte les fichiers
cq.exporters.export(assembly, 'hook_lock_3D_model.step')
cq.exporters.export(assembly, 'hook_lock_3D_model.stl')

# ✅ Affiche dans CQ-editor (optionnel)
show_object(assembly)
