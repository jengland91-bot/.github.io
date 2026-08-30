// Rise Above — Streamer.bot Execute C# Code
//
// One action runs every chat command. Create this action, paste this file,
// then add Command triggers: !race !dual !replay !grid !desk !brb !ending
// !starting !face !room !rig !wheel !pedals !game
//
// Streamer.bot → Stream Apps → Meld Studio → Add connection 127.0.0.1
// Meld Studio → Settings → Advanced → Allow remote connections

using System;
using System.Collections.Generic;

string raw = "";
if (args.ContainsKey("command")) raw = args["command"].ToString();
else if (args.ContainsKey("input0")) raw = args["input0"].ToString();
else if (args.ContainsKey("rawInput")) raw = args["rawInput"].ToString();
else if (args.ContainsKey("message")) raw = args["message"].ToString();

raw = (raw ?? "").Trim();
if (raw.StartsWith("!")) raw = raw.Substring(1);
int space = raw.IndexOf(' ');
if (space > 0) raw = raw.Substring(0, space);
raw = raw.ToLowerInvariant();

string[] liveScenes = { "RACE", "GRID", "RACE DUAL", "DESK" };

void ShowScene(string scene)
{
    CPH.MeldStudioShowSceneByName(scene);
}

void SetCams(bool face, bool room, bool wheel, bool pedals)
{
    foreach (string scene in liveScenes)
    {
        if (face) CPH.MeldStudioShowLayerByName(scene, "Cam / Face");
        else CPH.MeldStudioHideLayerByName(scene, "Cam / Face");

        if (room) CPH.MeldStudioShowLayerByName(scene, "Cam / Room");
        else CPH.MeldStudioHideLayerByName(scene, "Cam / Room");

        if (scene == "DESK")
        {
            continue;
        }

        if (wheel) CPH.MeldStudioShowLayerByName(scene, "Cam / Wheel");
        else CPH.MeldStudioHideLayerByName(scene, "Cam / Wheel");

        if (pedals) CPH.MeldStudioShowLayerByName(scene, "Cam / Pedals");
        else CPH.MeldStudioHideLayerByName(scene, "Cam / Pedals");
    }
}

switch (raw)
{
    case "race":
    case "live":
        ShowScene("RACE");
        break;
    case "dual":
        ShowScene("RACE DUAL");
        break;
    case "replay":
        ShowScene("REPLAY");
        break;
    case "grid":
        ShowScene("GRID");
        break;
    case "desk":
        ShowScene("DESK");
        break;
    case "brb":
        ShowScene("BRB");
        break;
    case "ending":
        ShowScene("ENDING");
        break;
    case "starting":
    case "soon":
        ShowScene("STARTING SOON");
        break;
    case "face":
        SetCams(true, false, false, false);
        break;
    case "room":
        SetCams(false, true, false, false);
        break;
    case "wheel":
        SetCams(false, false, true, false);
        break;
    case "pedals":
        SetCams(false, false, false, true);
        break;
    case "rig":
        SetCams(true, true, true, true);
        break;
    case "game":
        SetCams(false, false, false, false);
        break;
    default:
        CPH.LogInfo("Rise Above: unknown command " + raw);
        break;
}
