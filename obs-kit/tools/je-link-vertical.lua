-- J England Live — link main scenes to Aitum Vertical scenes.
-- OBS → Tools → Scripts → + → pick this file. Run once after Load scenes.
-- Safe to leave enabled.

obs = obslua

local LINK_MAP = {
  ["STARTING SOON"] = "STARTING SOON",
  ["JUST CHATTING"] = "JUST CHATTING",
  ["IRL"] = "JUST CHATTING",
  ["GAMING"] = "PLAYING",
  ["SIM"] = "PLAYING",
  ["SIM RIG"] = "PLAYING",
  ["DUAL"] = "PLAYING",
  ["REPLAY"] = "PLAYING",
  ["BRB"] = "BRB",
  ["ENDING"] = "ENDING",
}

function script_description()
  return "J England: write Aitum Linked Scenes (main → vertical) so Shorts follows your widescreen clicks."
end

function apply_links()
  for main_name, vert_name in pairs(LINK_MAP) do
    local source = obs.obs_get_source_by_name(main_name)
    if source ~= nil then
      local settings = obs.obs_source_get_settings(source)
      local arr = obs.obs_data_array_create()
      local item = obs.obs_data_create()
      -- Empty name + 1080x1920 matches Aitum Vertical by size
      obs.obs_data_set_string(item, "name", "")
      obs.obs_data_set_int(item, "width", 1080)
      obs.obs_data_set_int(item, "height", 1920)
      obs.obs_data_set_string(item, "scene", vert_name)
      obs.obs_data_array_push_back(arr, item)
      obs.obs_data_set_array(settings, "canvas", arr)
      obs.obs_source_update(source, settings)
      obs.obs_data_release(item)
      obs.obs_data_array_release(arr)
      obs.obs_data_release(settings)
      obs.obs_source_release(source)
      print("[J England] Linked " .. main_name .. " → " .. vert_name)
    end
  end
end

function script_load(settings)
  apply_links()
end

function script_update(settings)
  apply_links()
end
