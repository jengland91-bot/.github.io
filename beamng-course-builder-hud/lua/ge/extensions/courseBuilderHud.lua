-- Course Builder HUD
-- Spawns course props from a UI app without opening World Editor (F11).
-- Props are session objects (spawned vehicles / physics props). Save a layout JSON
-- to reload them later; for permanent map edits still use World Editor + Prefabs.

local M = {}

local placed = {}          -- { id, kind, model, config, pos, rotYaw }
local nextId = 1
local currentYaw = 0       -- degrees
local snapDegrees = 15
local placeDistance = 12   -- fallback metres ahead of camera if ray misses
local saveDir = "settings/courseBuilderHud"

-- Stock spawnable props (same family as Esc → Vehicles → Props).
-- Folder names follow BeamNG vehicle packs; adjust if a spawn fails on your version.
local PROP_CATALOG = {
  { id = "cone",            label = "Traffic Cone",       model = "cones",              config = nil },
  { id = "cardboard",       label = "Cardboard Box",      model = "cardboard_box",      config = nil },
  { id = "steel_barrel",    label = "Steel Barrel",       model = "barrels",            config = nil },
  { id = "traffic_barrel",  label = "Traffic Barrel",     model = "trafficbarrel",      config = nil },
  { id = "concrete_barrier",label = "Concrete Barrier",   model = "barrier",            config = nil },
  { id = "plastic_barrier", label = "Plastic Barrier",    model = "plastic_barrier",    config = nil },
  { id = "soft_barrier",    label = "Soft Track Barrier", model = "softbarrier",        config = nil },
  { id = "crowd_barrier",   label = "Crowd Barrier",      model = "crowd_barrier",      config = nil },
  { id = "tirewall",        label = "Tire Wall",          model = "tirewall",           config = nil },
  { id = "tirestacks",      label = "Tire Stacks",        model = "tirestacks",         config = nil },
  { id = "bollard",         label = "Bollard",            model = "bollard",            config = nil },
  { id = "sawhorse",        label = "Saw Horse",          model = "sawhorse",           config = nil },
  { id = "delineator",      label = "Delineator Post",    model = "delineator",         config = nil },
  { id = "bin",             label = "Bin",                model = "bin",                config = nil },
  { id = "woodcrate",       label = "Wood Crate",         model = "woodcrate",          config = nil },
}

local selectedPropId = PROP_CATALOG[1].id

local function logI(msg)
  log("I", "courseBuilderHud", tostring(msg))
end

local function logE(msg)
  log("E", "courseBuilderHud", tostring(msg))
end

local function notify(msg)
  guihooks.trigger("toastrMsg", { type = "info", title = "Course Builder", msg = tostring(msg) })
end

local function findProp(propId)
  for _, p in ipairs(PROP_CATALOG) do
    if p.id == propId then return p end
  end
  return PROP_CATALOG[1]
end

local function yawToQuat(yawDeg)
  return quatFromEuler(0, 0, math.rad(yawDeg or 0))
end

--- Ray from free camera / vehicle cam into the world; returns vec3 or nil
local function aimPoint()
  local camPos = vec3(getCameraPosition())
  local q = quat(getCameraQuat())
  -- BeamNG camera forward is typically +Y in camera space
  local dir = q * vec3(0, 1, 0)
  dir = dir:normalized()

  local from = camPos + dir * 0.5
  local to = camPos + dir * 200

  local ok, hit = pcall(function()
    return Engine.castRay(from, to, true, true)
  end)

  if ok and hit and hit.pt then
    return vec3(hit.pt)
  end

  -- Fallback: flat distance ahead of camera, drop to surface if possible
  local fallback = camPos + dir * placeDistance
  local ok2, surfaceZ = pcall(function()
    return be:getSurfaceHeightBelow(fallback)
  end)
  if ok2 and surfaceZ and surfaceZ == surfaceZ then
    fallback.z = surfaceZ + 0.05
  end
  return fallback
end

local function pushUiState()
  local list = {}
  for _, e in ipairs(placed) do
    list[#list + 1] = {
      id = e.id,
      label = e.label,
      model = e.model,
    }
  end
  guihooks.trigger("CourseBuilderHudState", {
    selectedPropId = selectedPropId,
    yaw = currentYaw,
    snap = snapDegrees,
    count = #placed,
    placed = list,
    catalog = PROP_CATALOG,
  })
end

local function trySpawn(model, opts)
  if not core_vehicles or not core_vehicles.spawnNewVehicle then
    return nil, "core_vehicles.spawnNewVehicle unavailable"
  end
  local ok, veh = pcall(function()
    return core_vehicles.spawnNewVehicle(model, opts)
  end)
  if ok and veh then
    return veh, nil
  end
  return nil, tostring(veh)
end

local function spawnVehicleProp(prop, pos, yaw)
  local rot = yawToQuat(yaw)
  local opts = { pos = pos, rot = rot }
  if prop.config then
    opts.config = prop.config
  end

  local veh, err = trySpawn(prop.model, opts)
  if not veh and prop.config then
    veh, err = trySpawn(prop.model, { pos = pos, rot = rot })
  end

  if not veh then
    logE("Failed to spawn " .. tostring(prop.model) .. ": " .. tostring(err))
    notify("Could not spawn " .. prop.label .. " — check model name in catalog")
    return nil
  end

  local obj = veh
  if type(veh) == "number" then
    obj = be:getObjectByID(veh)
  end

  if obj and obj.setPositionRotation then
    obj:setPositionRotation(pos.x, pos.y, pos.z, rot.x, rot.y, rot.z, rot.w)
  end

  return obj
end

local function placeSelected()
  local prop = findProp(selectedPropId)
  local pos = aimPoint()
  if not pos then
    notify("No aim point")
    return
  end

  local obj = spawnVehicleProp(prop, pos, currentYaw)
  if not obj then return end

  local entry = {
    id = nextId,
    kind = "vehicle",
    label = prop.label,
    model = prop.model,
    config = prop.config,
    propId = prop.id,
    pos = { x = pos.x, y = pos.y, z = pos.z },
    rotYaw = currentYaw,
    objId = obj.getID and obj:getID() or nil,
  }
  nextId = nextId + 1
  placed[#placed + 1] = entry
  notify("Placed " .. prop.label)
  pushUiState()
end

local function deleteObjectByEntry(entry)
  if not entry then return end
  if entry.objId then
    local obj = be:getObjectByID(entry.objId)
    if obj then
      obj:delete()
      return
    end
  end
  -- Fallback: find by scanning recent spawned vehicles is unreliable; skip
end

local function undoLast()
  local entry = table.remove(placed)
  if not entry then
    notify("Nothing to undo")
    return
  end
  deleteObjectByEntry(entry)
  notify("Undid " .. tostring(entry.label))
  pushUiState()
end

local function clearAll()
  for i = #placed, 1, -1 do
    deleteObjectByEntry(placed[i])
    placed[i] = nil
  end
  placed = {}
  notify("Cleared course props")
  pushUiState()
end

local function rotateYaw(delta)
  currentYaw = (currentYaw + (delta or snapDegrees)) % 360
  if currentYaw < 0 then currentYaw = currentYaw + 360 end
  pushUiState()
end

local function setYaw(yaw)
  currentYaw = tonumber(yaw) or 0
  pushUiState()
end

local function setSnap(snap)
  snapDegrees = tonumber(snap) or 15
  pushUiState()
end

local function selectProp(propId)
  selectedPropId = tostring(propId or selectedPropId)
  pushUiState()
end

local function ensureSaveDir()
  if not FS:directoryExists(saveDir) then
    FS:directoryCreate(saveDir)
  end
end

local function serializeLayout()
  local items = {}
  for _, e in ipairs(placed) do
    items[#items + 1] = {
      propId = e.propId,
      model = e.model,
      config = e.config,
      label = e.label,
      pos = e.pos,
      rotYaw = e.rotYaw,
    }
  end
  return {
    version = 1,
    name = "course",
    items = items,
  }
end

local function saveLayout(name)
  name = tostring(name or "course"):gsub("[^%w%-%_]", "_")
  if name == "" then name = "course" end
  ensureSaveDir()
  local path = saveDir .. "/" .. name .. ".json"
  local data = serializeLayout()
  data.name = name
  local ok = jsonWriteFile(path, data, true)
  if ok == false then
    -- older API returns nil on success sometimes; also try writeFile
    local encoded = jsonEncode(data)
    writeFile(path, encoded)
  end
  notify("Saved " .. path)
  pushUiState()
  return path
end

local function loadLayout(name)
  name = tostring(name or "course"):gsub("[^%w%-%_]", "_")
  local path = saveDir .. "/" .. name .. ".json"
  if not FS:fileExists(path) then
    notify("No save: " .. path)
    return
  end

  local data = jsonReadFile(path)
  if not data or not data.items then
    notify("Bad save file")
    return
  end

  clearAll()

  for _, item in ipairs(data.items) do
    local prop = findProp(item.propId)
    -- Prefer saved model/config over catalog defaults
    prop = {
      id = item.propId or prop.id,
      label = item.label or prop.label,
      model = item.model or prop.model,
      config = item.config or prop.config,
    }
    local pos = vec3(item.pos.x, item.pos.y, item.pos.z)
    local yaw = item.rotYaw or 0
    local obj = spawnVehicleProp(prop, pos, yaw)
    if obj then
      placed[#placed + 1] = {
        id = nextId,
        kind = "vehicle",
        label = prop.label,
        model = prop.model,
        config = prop.config,
        propId = prop.id,
        pos = { x = pos.x, y = pos.y, z = pos.z },
        rotYaw = yaw,
        objId = obj.getID and obj:getID() or nil,
      }
      nextId = nextId + 1
    end
  end

  notify("Loaded " .. #placed .. " props from " .. name)
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
  guihooks.trigger("CourseBuilderHudSaves", names)
  return names
end

-- Public API (called from UI via bngApi.engineLua)
M.place = placeSelected
M.undo = undoLast
M.clear = clearAll
M.rotate = rotateYaw
M.setYaw = setYaw
M.setSnap = setSnap
M.selectProp = selectProp
M.save = saveLayout
M.load = loadLayout
M.listSaves = listSaves
M.refresh = pushUiState

M.getCatalog = function()
  return PROP_CATALOG
end

local function onExtensionLoaded()
  logI("Course Builder HUD loaded")
  pushUiState()
end

local function onExtensionUnloaded()
  logI("Course Builder HUD unloaded")
end

M.onExtensionLoaded = onExtensionLoaded
M.onExtensionUnloaded = onExtensionUnloaded

return M
