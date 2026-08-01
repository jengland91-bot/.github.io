-- Course Builder HUD v2
-- Freeroam placement tool: props, rocks, nature, static meshes — no F11 required.
-- Save layouts as JSON; use F11 Prefab only when you want permanent map content.

local M = {}

local placed = {}
local nextId = 1
local currentYaw = 0
local currentScale = 1
local snapDegrees = 15
local nudgeStep = 0.5
local placeDistance = 14
local saveDir = "settings/courseBuilderHud"
local selectedPropId = "cone"
local selectedPlacedId = nil
local activeCategory = "course"
local mode = "place" -- place | edit

-- Easy tools
local paintMode = false      -- auto-place while aiming when spacing exceeded
local paintHeld = false      -- true while paint hotkey held
local paintSpacing = 3.0     -- metres between paint drops
local lastPaintPos = nil
local gridSnap = false
local gridSize = 1.0
local ghostEnabled = false   -- off by default; turn on from HUD or Alt+H while placing
local hudOpen = false        -- true only while Course Builder UI app is on screen
local randomYaw = false
local randomScale = false
local randomScaleMin = 0.8
local randomScaleMax = 1.3
local favorites = {}         -- [propId] = true
local lastAimPos = nil
local uiDirtyTimer = 0
local ghostActiveUntil = 0   -- auto-hide ghost shortly after you stop placing

-- kind: "vehicle" uses core_vehicles; "static" uses TSStatic shapeName
local BASE_CATALOG = {
  -- Course
  { id = "cone",             label = "Traffic Cone",        category = "course",  kind = "vehicle", model = "cones" },
  { id = "delineator",       label = "Delineator",          category = "course",  kind = "vehicle", model = "delineator" },
  { id = "traffic_barrel",   label = "Traffic Barrel",      category = "course",  kind = "vehicle", model = "trafficbarrel" },
  { id = "soft_barrier",     label = "Soft Track Barrier",  category = "course",  kind = "vehicle", model = "softbarrier" },
  { id = "crowd_barrier",    label = "Crowd Barrier",       category = "course",  kind = "vehicle", model = "crowd_barrier" },
  { id = "plastic_barrier",  label = "Plastic Barrier",     category = "course",  kind = "vehicle", model = "plastic_barrier" },
  { id = "concrete_barrier", label = "Concrete Barrier",    category = "course",  kind = "vehicle", model = "barrier" },
  { id = "tirewall",         label = "Tire Wall",           category = "course",  kind = "vehicle", model = "tirewall" },
  { id = "tirestacks",       label = "Tire Stacks",         category = "course",  kind = "vehicle", model = "tirestacks" },
  { id = "sawhorse",         label = "Saw Horse",           category = "course",  kind = "vehicle", model = "sawhorse" },
  { id = "bollard",          label = "Bollard",             category = "course",  kind = "vehicle", model = "bollard" },

  -- Rocks & nature (physics props when installed)
  { id = "rocks",            label = "Rocks & Boulders",    category = "rocks",   kind = "vehicle", model = "rocks" },
  { id = "rock",             label = "Rock",                category = "rocks",   kind = "vehicle", model = "rock" },
  { id = "boulder",          label = "Boulder",             category = "rocks",   kind = "vehicle", model = "boulder" },
  { id = "logs",             label = "Logs",                category = "nature",  kind = "vehicle", model = "logs" },
  { id = "woodcrate",        label = "Wood Crate",          category = "nature",  kind = "vehicle", model = "woodcrate" },
  { id = "woodplanks",       label = "Wood Planks",         category = "nature",  kind = "vehicle", model = "woodplanks" },
  { id = "bales",            label = "Bales",               category = "nature",  kind = "vehicle", model = "bales" },

  -- Obstacles / clutter
  { id = "steel_barrel",     label = "Steel Barrel",        category = "clutter", kind = "vehicle", model = "barrels" },
  { id = "cardboard",        label = "Cardboard Box",       category = "clutter", kind = "vehicle", model = "cardboard_box" },
  { id = "bin",              label = "Bin",                 category = "clutter", kind = "vehicle", model = "bin" },
  { id = "metalbox",         label = "Metal Box",           category = "clutter", kind = "vehicle", model = "metalbox" },
  { id = "fridge",           label = "Fridge",              category = "clutter", kind = "vehicle", model = "fridge" },
  { id = "shipping",         label = "Shipping Container",  category = "clutter", kind = "vehicle", model = "container" },

  -- Static meshes (no physics jbeam) — common shared shapes; may vary by install
  { id = "static_rock_a",    label = "Static Rock A",       category = "static",  kind = "static",  shape = "levels/west_coast_usa/art/shapes/rocks/rock_medium_a.dae", scale = 1 },
  { id = "static_rock_b",    label = "Static Rock B",       category = "static",  kind = "static",  shape = "levels/west_coast_usa/art/shapes/rocks/rock_large_a.dae", scale = 1 },
  { id = "static_rock_c",    label = "Static Boulder",      category = "static",  kind = "static",  shape = "levels/west_coast_usa/art/shapes/rocks/boulder_a.dae", scale = 1 },
}

local CATEGORIES = {
  { id = "favs",    label = "Favs" },
  { id = "course",  label = "Course" },
  { id = "rocks",   label = "Rocks" },
  { id = "nature",  label = "Nature" },
  { id = "clutter", label = "Clutter" },
  { id = "static",  label = "Static" },
  { id = "found",   label = "Found" },
}

local catalog = {}

local function logI(msg) log("I", "courseBuilderHud", tostring(msg)) end
local function logE(msg) log("E", "courseBuilderHud", tostring(msg)) end

local function notify(msg, typ)
  guihooks.trigger("toastrMsg", {
    type = typ or "info",
    title = "Course Builder",
    msg = tostring(msg),
  })
end

local function yawToQuat(yawDeg)
  return quatFromEuler(0, 0, math.rad(yawDeg or 0))
end

local function copyCatalogEntry(p)
  return {
    id = p.id,
    label = p.label,
    category = p.category,
    kind = p.kind or "vehicle",
    model = p.model,
    config = p.config,
    shape = p.shape,
    scale = p.scale,
  }
end

local function rebuildCatalog(discovered)
  catalog = {}
  local seen = {}
  for _, p in ipairs(BASE_CATALOG) do
    catalog[#catalog + 1] = copyCatalogEntry(p)
    seen[p.id] = true
  end
  if discovered then
    for _, p in ipairs(discovered) do
      if p.id and not seen[p.id] then
        catalog[#catalog + 1] = copyCatalogEntry(p)
        seen[p.id] = true
      end
    end
  end
end

rebuildCatalog()

local function findProp(propId)
  for _, p in ipairs(catalog) do
    if p.id == propId then return p end
  end
  return catalog[1]
end

local function findPlaced(id)
  id = tonumber(id)
  for _, e in ipairs(placed) do
    if e.id == id then return e end
  end
  return nil
end

local function getObject(entry)
  if not entry or not entry.objId then return nil end
  return be:getObjectByID(entry.objId)
end

local function aimPoint()
  local camPos = vec3(getCameraPosition())
  local q = quat(getCameraQuat())
  local dir = (q * vec3(0, 1, 0)):normalized()
  local from = camPos + dir * 0.4
  local to = camPos + dir * 250

  local ok, hit = pcall(function()
    return Engine.castRay(from, to, true, true)
  end)
  if ok and hit and hit.pt then
    return vec3(hit.pt), dir
  end

  local fallback = camPos + dir * placeDistance
  local ok2, surfaceZ = pcall(function()
    return be:getSurfaceHeightBelow(fallback)
  end)
  if ok2 and type(surfaceZ) == "number" and surfaceZ == surfaceZ then
    fallback.z = surfaceZ + 0.05
  end
  return fallback, dir
end

local function catalogForUi()
  local out = {}
  for _, p in ipairs(catalog) do
    out[#out + 1] = {
      id = p.id,
      label = p.label,
      category = p.category,
      kind = p.kind,
      favorite = favorites[p.id] == true,
    }
  end
  table.sort(out, function(a, b)
    if a.favorite ~= b.favorite then return a.favorite end
    return tostring(a.label) < tostring(b.label)
  end)
  return out
end

local function placedForUi()
  local out = {}
  for _, e in ipairs(placed) do
    out[#out + 1] = {
      id = e.id,
      label = e.label,
      kind = e.kind,
      category = e.category,
    }
  end
  return out
end

local function pushUiState()
  guihooks.trigger("CourseBuilderHudState", {
    selectedPropId = selectedPropId,
    selectedPlacedId = selectedPlacedId,
    yaw = currentYaw,
    scale = currentScale,
    snap = snapDegrees,
    nudge = nudgeStep,
    count = #placed,
    mode = mode,
    category = activeCategory,
    categories = CATEGORIES,
    catalog = catalogForUi(),
    placed = placedForUi(),
    paintMode = paintMode,
    paintHeld = paintHeld,
    paintSpacing = paintSpacing,
    gridSnap = gridSnap,
    gridSize = gridSize,
    ghostEnabled = ghostEnabled,
    randomYaw = randomYaw,
    randomScale = randomScale,
  })
end

local function trySpawnVehicle(model, opts)
  if not core_vehicles or not core_vehicles.spawnNewVehicle then
    return nil, "spawn API missing"
  end
  local ok, veh = pcall(function()
    return core_vehicles.spawnNewVehicle(model, opts)
  end)
  if ok and veh then return veh end
  return nil, tostring(veh)
end

local function applyTransform(obj, pos, yaw, scale)
  if not obj then return end
  local rot = yawToQuat(yaw)
  if obj.setPositionRotation then
    obj:setPositionRotation(pos.x, pos.y, pos.z, rot.x, rot.y, rot.z, rot.w)
  elseif obj.setPosRot then
    obj:setPosRot(pos.x, pos.y, pos.z, rot.x, rot.y, rot.z, rot.w)
  end
  if scale and scale ~= 1 and obj.scale ~= nil then
    obj.scale = vec3(scale, scale, scale)
  end
end

local function spawnVehicleProp(prop, pos, yaw, scale)
  local rot = yawToQuat(yaw)
  local opts = { pos = pos, rot = rot }
  if prop.config then opts.config = prop.config end

  local veh, err = trySpawnVehicle(prop.model, opts)
  if not veh then
    logE("Vehicle spawn failed " .. tostring(prop.model) .. ": " .. tostring(err))
    return nil
  end

  local obj = type(veh) == "number" and be:getObjectByID(veh) or veh
  applyTransform(obj, pos, yaw, scale or 1)
  return obj
end

local function spawnStaticProp(prop, pos, yaw, scale)
  local shape = prop.shape
  if not shape or shape == "" then
    notify("No mesh path for " .. tostring(prop.label), "error")
    return nil
  end

  local obj = createObject("TSStatic")
  if not obj then
    notify("Could not create static object", "error")
    return nil
  end

  obj:setField("shapeName", 0, shape)
  obj:setField("collisionType", 0, "Visible Mesh Final")
  obj:setField("decalType", 0, "Visible Mesh Final")
  obj:setField("playAmbient", 0, "0")
  obj.canSave = false

  local name = "cbh_static_" .. tostring(nextId)
  local okReg = pcall(function()
    obj:registerObject(name)
  end)
  if not okReg then
    logE("registerObject failed for " .. name)
  end

  pcall(function()
    if scenetree and scenetree.MissionGroup then
      scenetree.MissionGroup:addObject(obj.obj or obj)
    end
  end)

  local s = scale or prop.scale or 1
  applyTransform(obj, pos, yaw, s)

  pcall(function()
    if be.reloadCollision then be:reloadCollision() end
  end)

  return obj
end

local function snapPosToGrid(pos)
  if not gridSnap or not pos then return pos end
  local g = gridSize
  if not g or g <= 0 then return pos end
  return vec3(
    math.floor(pos.x / g + 0.5) * g,
    math.floor(pos.y / g + 0.5) * g,
    pos.z
  )
end

local function markGhostActive(seconds)
  ghostActiveUntil = os.clock() + (tonumber(seconds) or 8)
end

local function ghostShouldShow()
  -- Never show the aim ball unless the Course Builder app is actually open
  if not hudOpen then return false end
  if not ghostEnabled then return false end
  if paintMode or paintHeld then return true end
  return os.clock() <= ghostActiveUntil
end

local function resolvePlaceYaw()
  if randomYaw then
    return math.random() * 360
  end
  return currentYaw
end

local function resolvePlaceScale()
  if randomScale then
    local a, b = randomScaleMin, randomScaleMax
    if b < a then a, b = b, a end
    return a + math.random() * (b - a)
  end
  return currentScale
end

local function trackEntry(prop, obj, pos, yaw, scale)
  local entry = {
    id = nextId,
    kind = prop.kind or "vehicle",
    label = prop.label,
    model = prop.model,
    config = prop.config,
    shape = prop.shape,
    propId = prop.id,
    category = prop.category,
    pos = { x = pos.x, y = pos.y, z = pos.z },
    rotYaw = yaw,
    scale = scale or 1,
    objId = (obj and obj.getID) and obj:getID() or nil,
  }
  nextId = nextId + 1
  placed[#placed + 1] = entry
  selectedPlacedId = entry.id
  lastPaintPos = vec3(pos.x, pos.y, pos.z)
  return entry
end

--- silent=true skips toast (used by paint mode)
local function placeSelected(silent)
  local prop = findProp(selectedPropId)
  if not prop then
    if not silent then notify("Pick something from the list", "warning") end
    return false
  end

  local pos = aimPoint()
  if not pos then
    if not silent then notify("No aim point", "warning") end
    return false
  end
  pos = snapPosToGrid(pos)

  local yaw = resolvePlaceYaw()
  local scale = resolvePlaceScale()
  local obj
  if prop.kind == "static" then
    obj = spawnStaticProp(prop, pos, yaw, scale)
  else
    obj = spawnVehicleProp(prop, pos, yaw, scale)
  end

  if not obj then
    if not silent then
      notify("Could not place " .. prop.label .. " (missing on this install?)", "error")
    end
    return false
  end

  trackEntry(prop, obj, pos, yaw, scale)
  if not randomYaw then currentYaw = yaw end
  if not randomScale then currentScale = scale end
  mode = "edit"
  markGhostActive(8)
  if not silent then notify("Placed " .. prop.label) end
  pushUiState()
  return true
end

local function deleteObjectByEntry(entry)
  local obj = getObject(entry)
  if obj then
    pcall(function() obj:delete() end)
  end
end

local function syncEntryFromObject(entry)
  local obj = getObject(entry)
  if not obj then return end
  local pos
  if obj.getPosition then
    pos = obj:getPosition()
  end
  if pos then
    entry.pos = { x = pos.x, y = pos.y, z = pos.z }
  end
end

local function applyEntryTransform(entry)
  local obj = getObject(entry)
  if not obj then
    notify("Object gone — re-place or undo", "warning")
    return false
  end
  local pos = vec3(entry.pos.x, entry.pos.y, entry.pos.z)
  applyTransform(obj, pos, entry.rotYaw, entry.scale or 1)
  if entry.kind == "static" then
    pcall(function()
      if be.reloadCollision then be:reloadCollision() end
    end)
  end
  return true
end

local function selectPlaced(id)
  local entry = findPlaced(id)
  if not entry then
    selectedPlacedId = nil
    pushUiState()
    return
  end
  selectedPlacedId = entry.id
  currentYaw = entry.rotYaw or 0
  currentScale = entry.scale or 1
  mode = "edit"
  pushUiState()
end

local function nudgeSelected(dx, dy, dz)
  local entry = findPlaced(selectedPlacedId)
  if not entry then
    notify("Select a placed item first", "warning")
    return
  end
  dx = tonumber(dx) or 0
  dy = tonumber(dy) or 0
  dz = tonumber(dz) or 0
  entry.pos.x = entry.pos.x + dx
  entry.pos.y = entry.pos.y + dy
  entry.pos.z = entry.pos.z + dz
  applyEntryTransform(entry)
  pushUiState()
end

local function nudgeRelative(forward, right, up)
  local entry = findPlaced(selectedPlacedId)
  if not entry then
    notify("Select a placed item first", "warning")
    return
  end
  forward = tonumber(forward) or 0
  right = tonumber(right) or 0
  up = tonumber(up) or 0

  local yaw = math.rad(entry.rotYaw or 0)
  local fx, fy = -math.sin(yaw), math.cos(yaw)
  local rx, ry = math.cos(yaw), math.sin(yaw)

  entry.pos.x = entry.pos.x + fx * forward + rx * right
  entry.pos.y = entry.pos.y + fy * forward + ry * right
  entry.pos.z = entry.pos.z + up
  applyEntryTransform(entry)
  pushUiState()
end

local function rotateSelected(delta)
  local entry = findPlaced(selectedPlacedId)
  if not entry then
    currentYaw = (currentYaw + (delta or snapDegrees)) % 360
    if currentYaw < 0 then currentYaw = currentYaw + 360 end
    pushUiState()
    return
  end
  entry.rotYaw = (entry.rotYaw + (delta or snapDegrees)) % 360
  if entry.rotYaw < 0 then entry.rotYaw = entry.rotYaw + 360 end
  currentYaw = entry.rotYaw
  applyEntryTransform(entry)
  pushUiState()
end

local function setSelectedScale(scale)
  scale = tonumber(scale) or 1
  if scale < 0.1 then scale = 0.1 end
  if scale > 20 then scale = 20 end
  currentScale = scale
  local entry = findPlaced(selectedPlacedId)
  if entry then
    entry.scale = scale
    applyEntryTransform(entry)
  end
  pushUiState()
end

local function deleteSelected()
  local id = selectedPlacedId
  if not id then
    notify("Nothing selected", "warning")
    return
  end
  for i, e in ipairs(placed) do
    if e.id == id then
      deleteObjectByEntry(e)
      table.remove(placed, i)
      selectedPlacedId = placed[#placed] and placed[#placed].id or nil
      notify("Deleted")
      pushUiState()
      return
    end
  end
end

local function duplicateSelected()
  local entry = findPlaced(selectedPlacedId)
  if not entry then
    notify("Select something to duplicate", "warning")
    return
  end
  local prop = findProp(entry.propId) or {
    id = entry.propId,
    label = entry.label,
    kind = entry.kind,
    model = entry.model,
    config = entry.config,
    shape = entry.shape,
    category = entry.category,
  }
  local pos = vec3(entry.pos.x + 1.5, entry.pos.y, entry.pos.z)
  local obj
  if entry.kind == "static" then
    obj = spawnStaticProp(prop, pos, entry.rotYaw, entry.scale)
  else
    obj = spawnVehicleProp(prop, pos, entry.rotYaw, entry.scale)
  end
  if not obj then
    notify("Duplicate failed", "error")
    return
  end
  trackEntry(prop, obj, pos, entry.rotYaw, entry.scale)
  notify("Duplicated " .. entry.label)
  pushUiState()
end

local function reaimSelected()
  local entry = findPlaced(selectedPlacedId)
  if not entry then
    notify("Select something first", "warning")
    return
  end
  local pos = aimPoint()
  entry.pos = { x = pos.x, y = pos.y, z = pos.z }
  applyEntryTransform(entry)
  notify("Moved to aim point")
  pushUiState()
end

local function undoLast()
  local entry = table.remove(placed)
  if not entry then
    notify("Nothing to undo", "warning")
    return
  end
  deleteObjectByEntry(entry)
  if selectedPlacedId == entry.id then
    selectedPlacedId = placed[#placed] and placed[#placed].id or nil
  end
  notify("Undid " .. tostring(entry.label))
  pushUiState()
end

local function clearAll()
  for i = #placed, 1, -1 do
    deleteObjectByEntry(placed[i])
    placed[i] = nil
  end
  placed = {}
  selectedPlacedId = nil
  notify("Cleared all placements")
  pushUiState()
end

local function setMode(m)
  mode = tostring(m or "place")
  pushUiState()
end

local function setCategory(cat)
  activeCategory = tostring(cat or "course")
  pushUiState()
end

local function rotateYaw(delta)
  rotateSelected(delta)
end

local function setYaw(yaw)
  currentYaw = tonumber(yaw) or 0
  local entry = findPlaced(selectedPlacedId)
  if entry then
    entry.rotYaw = currentYaw
    applyEntryTransform(entry)
  end
  pushUiState()
end

local function setSnap(snap)
  snapDegrees = tonumber(snap) or 15
  pushUiState()
end

local function setNudge(step)
  nudgeStep = tonumber(step) or 0.5
  pushUiState()
end

local function selectProp(propId)
  selectedPropId = tostring(propId or selectedPropId)
  mode = "place"
  markGhostActive(8)
  pushUiState()
end

local function ensureSaveDir()
  if not FS:directoryExists(saveDir) then
    FS:directoryCreate(saveDir)
  end
end

local function serializeLayout(name)
  local items = {}
  for _, e in ipairs(placed) do
    syncEntryFromObject(e)
    items[#items + 1] = {
      propId = e.propId,
      kind = e.kind,
      model = e.model,
      config = e.config,
      shape = e.shape,
      label = e.label,
      category = e.category,
      pos = e.pos,
      rotYaw = e.rotYaw,
      scale = e.scale,
    }
  end
  return {
    version = 2,
    name = name or "course",
    items = items,
  }
end

local function saveLayout(name)
  name = tostring(name or "course"):gsub("[^%w%-%_]", "_")
  if name == "" then name = "course" end
  ensureSaveDir()
  local path = saveDir .. "/" .. name .. ".json"
  local data = serializeLayout(name)
  local ok = jsonWriteFile(path, data, true)
  if ok == false then
    writeFile(path, jsonEncode(data))
  end
  notify("Saved " .. name)
  pushUiState()
  return path
end

local function spawnFromItem(item)
  local prop = findProp(item.propId)
  prop = {
    id = item.propId or (prop and prop.id),
    label = item.label or (prop and prop.label) or "Item",
    kind = item.kind or (prop and prop.kind) or "vehicle",
    model = item.model or (prop and prop.model),
    config = item.config or (prop and prop.config),
    shape = item.shape or (prop and prop.shape),
    category = item.category or (prop and prop.category),
  }
  local pos = vec3(item.pos.x, item.pos.y, item.pos.z)
  local yaw = item.rotYaw or 0
  local scale = item.scale or 1
  local obj
  if prop.kind == "static" then
    obj = spawnStaticProp(prop, pos, yaw, scale)
  else
    obj = spawnVehicleProp(prop, pos, yaw, scale)
  end
  if obj then
    trackEntry(prop, obj, pos, yaw, scale)
    return true
  end
  return false
end

local function loadLayout(name)
  name = tostring(name or "course"):gsub("[^%w%-%_]", "_")
  local path = saveDir .. "/" .. name .. ".json"
  if not FS:fileExists(path) then
    notify("No save named " .. name, "warning")
    return
  end
  local data = jsonReadFile(path)
  if not data or not data.items then
    notify("Bad save file", "error")
    return
  end

  clearAll()
  local okCount = 0
  for _, item in ipairs(data.items) do
    if spawnFromItem(item) then okCount = okCount + 1 end
  end
  notify("Loaded " .. okCount .. " / " .. #data.items .. " from " .. name)
  pushUiState()
end

local function listSaves()
  ensureSaveDir()
  local files = FS:findFiles(saveDir, "*.json", -1, true, false) or {}
  local names = {}
  for _, f in ipairs(files) do
    local n = f:match("([^/\\]+)%.json$")
    if n then names[#names + 1] = n end
  end
  table.sort(names)
  guihooks.trigger("CourseBuilderHudSaves", names)
  return names
end

local function exportPrefabNotes(name)
  name = tostring(name or "course"):gsub("[^%w%-%_]", "_")
  ensureSaveDir()
  local layoutPath = saveLayout(name)
  local guidePath = saveDir .. "/" .. name .. "_PREFAB.txt"
  local lines = {
    "Course Builder → Prefab guide",
    "1. Load this layout in freeroam (or keep current placements).",
    "2. Press F11 to open World Editor.",
    "3. In Scene Tree, select the spawned objects (Spawned Vehicles / cbh_static_*).",
    "4. Toolbar: Make selection a Prefab.",
    "5. Save prefab under your level art/prefabs folder.",
    "Layout JSON: " .. tostring(layoutPath),
    "Placed count: " .. tostring(#placed),
  }
  writeFile(guidePath, table.concat(lines, "\n"))
  notify("Saved layout + prefab guide")
  return guidePath
end

-- Discover rock/nature models from whatever is installed
local function looksNature(key, name)
  local s = string.lower(tostring(key or "") .. " " .. tostring(name or ""))
  if s:find("rock", 1, true) or s:find("boulder", 1, true) then return "rocks" end
  if s:find("log", 1, true) or s:find("wood", 1, true) or s:find("bale", 1, true) then return "nature" end
  if s:find("barrier", 1, true) or s:find("cone", 1, true) or s:find("tire", 1, true) then return "course" end
  return nil
end

local function scanInstalledProps()
  local discovered = {}
  local ok, list = pcall(function()
    if core_vehicles and core_vehicles.getModelList then
      return core_vehicles.getModelList(true)
    end
    return nil
  end)

  if not ok or not list then
    notify("Could not scan vehicle/prop list", "warning")
    rebuildCatalog()
    pushUiState()
    return
  end

  local models = list.models or list
  if type(models) ~= "table" then
    notify("Unexpected model list format", "warning")
    return
  end

  -- array form from getModelList(true)
  local count = 0
  for _, m in pairs(models) do
    if type(m) == "table" then
      local key = m.key or m.model or m.name
      local nice = m.Name or m.name or key
      local cat = looksNature(key, nice)
      if cat and key then
        local id = "found_" .. tostring(key)
        discovered[#discovered + 1] = {
          id = id,
          label = tostring(nice),
          category = "found",
          kind = "vehicle",
          model = tostring(key),
        }
        count = count + 1
      end
    elseif type(m) == "string" then
      local cat = looksNature(m, m)
      if cat then
        discovered[#discovered + 1] = {
          id = "found_" .. m,
          label = m,
          category = "found",
          kind = "vehicle",
          model = m,
        }
        count = count + 1
      end
    end
  end

  -- Also try dictionary form getModelList()
  if count == 0 then
    local ok2, dict = pcall(function() return core_vehicles.getModelList() end)
    if ok2 and type(dict) == "table" then
      for key, meta in pairs(dict) do
        local nice = (type(meta) == "table" and (meta.Name or meta.name)) or key
        if looksNature(key, nice) then
          discovered[#discovered + 1] = {
            id = "found_" .. tostring(key),
            label = tostring(nice),
            category = "found",
            kind = "vehicle",
            model = tostring(key),
          }
          count = count + 1
        end
      end
    end
  end

  rebuildCatalog(discovered)
  activeCategory = "found"
  notify("Found " .. count .. " rock/nature-related props")
  pushUiState()
end

-- Public API
M.place = function() placeSelected(false) end
M.undo = undoLast
M.clear = clearAll
M.rotate = rotateYaw
M.setYaw = setYaw
M.setSnap = setSnap
M.setNudge = setNudge
M.selectProp = selectProp
M.selectPlaced = selectPlaced
M.deleteSelected = deleteSelected
M.duplicateSelected = duplicateSelected
M.reaimSelected = reaimSelected
M.nudge = nudgeSelected
M.nudgeRel = nudgeRelative
M.setScale = setSelectedScale
M.setMode = setMode
M.setCategory = setCategory
M.scan = scanInstalledProps
M.save = saveLayout
M.load = loadLayout
M.listSaves = listSaves
M.exportPrefab = exportPrefabNotes
M.refresh = pushUiState

local function favPath()
  return saveDir .. "/favorites.json"
end

local function loadFavorites()
  ensureSaveDir()
  favorites = {}
  if FS:fileExists(favPath()) then
    local data = jsonReadFile(favPath())
    if type(data) == "table" then
      for _, id in ipairs(data) do
        favorites[tostring(id)] = true
      end
    end
  end
end

local function saveFavorites()
  ensureSaveDir()
  local list = {}
  for id, on in pairs(favorites) do
    if on then list[#list + 1] = id end
  end
  table.sort(list)
  jsonWriteFile(favPath(), list, true)
end

local function toggleFavorite(propId)
  propId = tostring(propId or selectedPropId)
  if favorites[propId] then
    favorites[propId] = nil
    notify("Removed favorite")
  else
    favorites[propId] = true
    notify("Favorited")
  end
  saveFavorites()
  pushUiState()
end

local function setPaintMode(on)
  paintMode = on and true or false
  if not paintMode then
    paintHeld = false
    lastPaintPos = nil
  end
  notify(paintMode and "Paint mode ON" or "Paint mode OFF")
  pushUiState()
end

local function togglePaintMode()
  setPaintMode(not paintMode)
end

local function setPaintHeld(on)
  paintHeld = on and true or false
  if paintHeld then
    lastPaintPos = nil
    placeSelected(true)
  end
  pushUiState()
end

local function setPaintSpacing(v)
  paintSpacing = math.max(0.5, tonumber(v) or 3)
  pushUiState()
end

local function setGridSnap(on)
  gridSnap = on and true or false
  notify(gridSnap and ("Grid " .. tostring(gridSize) .. "m") or "Grid off")
  pushUiState()
end

local function toggleGridSnap()
  setGridSnap(not gridSnap)
end

local function setGridSize(v)
  gridSize = math.max(0.25, tonumber(v) or 1)
  pushUiState()
end

local function setGhost(on)
  ghostEnabled = on and true or false
  if ghostEnabled then
    markGhostActive(12)
    notify("Ghost ON — only while app is open")
  else
    ghostActiveUntil = 0
    notify("Ghost OFF")
  end
  pushUiState()
end

local function toggleGhost()
  setGhost(not ghostEnabled)
end

local function setHudOpen(on)
  hudOpen = on and true or false
  if not hudOpen then
    -- App closed/removed: kill ghost immediately
    ghostActiveUntil = 0
    paintHeld = false
  else
    pushUiState()
  end
end

local function setRandomYaw(on)
  randomYaw = on and true or false
  pushUiState()
end

local function setRandomScale(on)
  randomScale = on and true or false
  pushUiState()
end

local function toggleRandomYaw()
  setRandomYaw(not randomYaw)
end

local function toggleRandomScale()
  setRandomScale(not randomScale)
end

local function maybePaintAtAim()
  if not (paintMode or paintHeld) then return end
  local pos = aimPoint()
  if not pos then return end
  pos = snapPosToGrid(pos)
  if lastPaintPos then
    local d = (pos - lastPaintPos):length()
    if d < paintSpacing then return end
  end
  placeSelected(true)
end

local function drawGhost()
  if not ghostShouldShow() then return end
  local pos = aimPoint()
  if not pos then return end
  pos = snapPosToGrid(pos)
  lastAimPos = pos

  local yaw = currentYaw
  local rad = math.rad(yaw)
  local fx, fy = -math.sin(rad), math.cos(rad)
  local tip = vec3(pos.x + fx * 1.2, pos.y + fy * 1.2, pos.z + 0.15)
  local col = ColorF(0.88, 0.64, 0.35, 0.65)
  local colLine = ColorF(0.95, 0.78, 0.45, 0.9)

  pcall(function()
    if debugDrawer then
      debugDrawer:drawSphere(pos + vec3(0, 0, 0.2), 0.35, col)
      debugDrawer:drawLine(pos + vec3(0, 0, 0.2), tip, colLine)
      if gridSnap then
        local g = gridSize
        local c = ColorF(0.88, 0.64, 0.35, 0.25)
        debugDrawer:drawLine(pos + vec3(-g, 0, 0.05), pos + vec3(g, 0, 0.05), c)
        debugDrawer:drawLine(pos + vec3(0, -g, 0.05), pos + vec3(0, g, 0.05), c)
      end
    end
  end)
end

M.toggleFavorite = toggleFavorite
M.setPaintMode = setPaintMode
M.togglePaintMode = togglePaintMode
M.setPaintHeld = setPaintHeld
M.setPaintSpacing = setPaintSpacing
M.setGridSnap = setGridSnap
M.toggleGridSnap = toggleGridSnap
M.setGridSize = setGridSize
M.setGhost = setGhost
M.toggleGhost = toggleGhost
M.setHudOpen = setHudOpen
M.setRandomYaw = setRandomYaw
M.setRandomScale = setRandomScale
M.toggleRandomYaw = toggleRandomYaw
M.toggleRandomScale = toggleRandomScale

-- Hotkey wrappers
M.hotkeyPlace = function() placeSelected(false) end
M.hotkeyUndo = undoLast
M.hotkeyDelete = deleteSelected
M.hotkeyRotateLeft = function() rotateYaw(-snapDegrees) end
M.hotkeyRotateRight = function() rotateYaw(snapDegrees) end
M.hotkeyPaintDown = function() setPaintHeld(true) end
M.hotkeyPaintUp = function() setPaintHeld(false) end

M.onUpdate = function(dtReal, dtSim, dtRaw)
  drawGhost()
  maybePaintAtAim()
end

M.onExtensionLoaded = function()
  logI("Course Builder HUD v2.1 loaded")
  rebuildCatalog()
  loadFavorites()
  pushUiState()
end

M.onExtensionUnloaded = function()
  paintHeld = false
  paintMode = false
  hudOpen = false
  ghostActiveUntil = 0
  logI("Course Builder HUD unloaded")
end

return M
