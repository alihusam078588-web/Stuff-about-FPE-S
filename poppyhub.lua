local function Notify()
  WindUI:Notify({
    Title = "announcement ",
    Content = "hi",
      Icon = "megaphone",
    Duration = 3
})
local anim = game:GetService("ReplicatedStorage").Events:FindFirstChild("AntiCheatTrigger")

if anim then
    anim:Destroy()
  print("removed AntiCheatTrigger")
end
local RunService = game:GetService("RunService")
local WindUI = loadstring(game:HttpGet("https://github.com/Footagesus/WindUI/releases/latest/download/main.lua"))()

WindUI:AddTheme({
    Name = "PoppyDarkPink",
    Background = Color3.fromHex("#160012"),
    Accent = Color3.fromHex("#ff03bc"),
    Outline = Color3.fromHex("#3d0032"),
    Text = Color3.fromHex("#ffffff"),
    Placeholder = Color3.fromHex("#8c6484"),
    Button = Color3.fromHex("#2d0024"),
    Icon = Color3.fromHex("#ff03bc"),
})

local Window = WindUI:CreateWindow({
    Title = "Poppyhub",
    Folder = "PoppyHub",
    Background = "rbxassetid://137443756121983",
    BackgroundImageTransparency = 0.32,
    Icon = "solar:compass-big-bold",
    Theme = "PoppyDarkPink",
    NewElements = true,
    HideSearchBar = false,
})

task.spawn(function()
    local targetUI = game:GetService("CoreGui"):FindFirstChild("PoppyHub") or game:GetService("Players").LocalPlayer:WaitForChild("PlayerGui")
    task.wait(0.2)
    for _, element in ipairs(targetUI:GetDescendants()) do
        if element:IsA("ImageLabel") and string.find(element.Image, "137443756121983") then
            element.ImageTransparency = 0.65
            element.ImageColor3 = Color3.fromRGB(140, 110, 130)
        end
    end
end)

Window:EditOpenButton({
    Title = "Poppyhub",
    Icon = "solar:compass-big-bold",
    CornerRadius = UDim.new(0, 16),
    StrokeThickness = 2,
    Color = ColorSequence.new(
        Color3.fromHex("#ff03bc"),
        Color3.fromHex("#590042")
    ),
    OnlyMobile = false,
    Enabled = true,
    Draggable = true,
})

local MainTab = Window:Tab({
    Title = "Main",
    Icon = "solar:home-2-bold",
    Border = true,
})

local SettingsTab = Window:Tab({
    Title = "Settings",
    Icon = "solar:settings-bold",
    Border = true,
})

local MainSection = MainTab:Section({
    Title = "Main Controls",
})

MainSection:Paragraph({
    Title = "Welcome to Poppyhub",
    Desc = "Configure your preferences and main features here.",
})

local WindowControlSection = SettingsTab:Section({
    Title = "Window Management",
})

WindowControlSection:Keybind({
    Flag = "UI_Toggle_Keybind",
    Title = "Toggle UI Keybind",
    Desc = "Press this key to open or close the Poppyhub interface",
    Value = "LeftControl",
    Callback = function(key)
        Window:SetToggleKey(Enum.KeyCode[key])
    end,
})

WindowControlSection:Button({
    Title = "Close / Destroy Window",
    Desc = "Completely removes the user interface from your screen",
    Color = Color3.fromHex("#ff03bc"),
    Icon = "solar:trash-bin-trash-bold",
    Callback = function()
        Window:Destroy()
    end,
})

local CustomizationSection = SettingsTab:Section({
    Title = "Theme & Customization",
})

CustomizationSection:Colorpicker({
    Flag = "PinkBackgroundTheme",
    Title = "Custom Pink Background Color",
    Desc = "Pick your favorite shade of pink for the UI panel background tint",
    Default = Color3.fromHex("#ff03bc"),
    Callback = function(color)
        print("Selected background color tint: ", tostring(color))
    end,
})

CustomizationSection:Toggle({
    Flag = "ToggleUIBackground",
    Title = "Toggle Panel Background Blur/Frame",
    Value = true,
    Callback = function(state)
        if Window.SetPanelBackground then
            Window:SetPanelBackground(state)
        end
    end,
})

CustomizationSection:Input({
    Flag = "CustomBackgroundImageID",
    Title = "Custom Background Image",
    Desc = "Input a custom Roblox Asset ID to change the frame graphic texture",
    Placeholder = "rbxassetid://123456789",
    Callback = function(assetId)
        print("Applying custom image texture asset ID: " .. assetId)
    end,
})

if not RunService:IsStudio() and writefile then
    local ConfigSection = SettingsTab:Section({
        Title = "Configuration Settings",
    })

    local ConfigManager = Window.ConfigManager
    local TargetConfigName = "default_poppy"

    local ConfigNameInput = ConfigSection:Input({
        Title = "New Config Name",
        Placeholder = "Enter configuration layout name...",
        Callback = function(value)
            TargetConfigName = value
        end,
    })

    ConfigSection:Space()

    local AllConfigs = ConfigManager:AllConfigs()
    local DefaultValue = table.find(AllConfigs, TargetConfigName) and TargetConfigName or nil

    local AllConfigsDropdown = ConfigSection:Dropdown({
        Title = "Select Config",
        Desc = "Choose an existing saved profile",
        Values = AllConfigs,
        Value = DefaultValue,
        Callback = function(value)
            TargetConfigName = value
            ConfigNameInput:Set(value)
        end
    })

    ConfigSection:Space()

    ConfigSection:Button({
        Title = "Save Configuration File",
        Justify = "Center",
        Callback = function()
            Window.CurrentConfig = ConfigManager:Config(TargetConfigName)
            if Window.CurrentConfig:Save() then
                WindUI:Notify({
                    Title = "Config Management",
                    Content = "Profile successfully saved as '" .. TargetConfigName .. "'!",
                })
                AllConfigsDropdown:Refresh(ConfigManager:AllConfigs())
            end
        end,
    })

    ConfigSection:Button({
        Title = "Load Configuration File",
        Justify = "Center",
        Callback = function()
            Window.CurrentConfig = ConfigManager:CreateConfig(TargetConfigName)
            if Window.CurrentConfig:Load() then
                WindUI:Notify({
                    Title = "Config Management",
                    Content = "Profile successfully applied from '" .. TargetConfigName .. "'!",
                })
            end
        end,
    })
end

do
    local ESPTab = Window:Tab({
        Title = "ESP",
        Icon = "solar:eye-bold",
        IconColor = Color3.fromRGB(255, 0, 0),
        Border = true,
    })

    local ESPSection = ESPTab:Section({
        Title = "ESP Controls",
        Desc = "Toggle ESP features for entities and objects",
        Box = true,
        BoxBorder = true,
        Opened = true,
    })

    local ESP = {
        Enabled = false,
        Monsters = {},
        Generators = {},
        Items = {},
        FakeElevator = nil,
        Connections = {},
        Settings = {
            ShowText = true,
            ShowTracer = true,
            ShowHighlight = true,
            ShowMonsters = true,
            ShowGenerators = true,
            ShowItems = true,
            ShowFakeElevator = true,
            MonstersColor = Color3.fromRGB(255, 0, 0),
            GeneratorsColor = Color3.fromRGB(0, 255, 0),
            ItemsColor = Color3.fromRGB(255, 255, 0),
            FakeElevatorColor = Color3.fromRGB(255, 0, 255),
            TextColor = Color3.new(1, 1, 1),
            TracerColor = Color3.new(1, 1, 1),
            HighlightColor = Color3.new(1, 1, 1),
            MaxDistance = 5000,
        }
    }

    local function countTable(t)
        local n = 0
        for _ in pairs(t) do n = n + 1 end
        return n
    end

    local function GetCurrentRoom()
        local currentRoom = workspace:FindFirstChild("CurrentRoom")
        if not currentRoom then return nil end
        return currentRoom:GetChildren()[1]
    end

    local function GetLocalCharacter()
        local player = game.Players.LocalPlayer
        return player and player.Character
    end

    local function GetHRP(character)
        return character and character:FindFirstChild("HumanoidRootPart")
    end

    local function WorldToScreen(position)
        local camera = workspace.CurrentCamera
        local screenPos, onScreen = camera:WorldToViewportPoint(position)
        return Vector2.new(screenPos.X, screenPos.Y), onScreen, screenPos.Z
    end

    local function CreateText()
        local text = Drawing.new("Text")
        text.Size = 14
        text.Font = 2
        text.Outline = true
        text.OutlineColor = Color3.new(0, 0, 0)
        text.Color = ESP.Settings.TextColor
        text.Center = true
        text.Visible = false
        return text
    end

    local function CreateTracer()
        local tracer = Drawing.new("Line")
        tracer.Thickness = 1.5
        tracer.Color = ESP.Settings.TracerColor
        tracer.Transparency = 1
        tracer.Visible = false
        return tracer
    end

    local function CreateHighlight(parent)
        local highlight = Instance.new("Highlight")
        highlight.FillColor = ESP.Settings.HighlightColor
        highlight.OutlineColor = Color3.new(1, 1, 1)
        highlight.FillTransparency = 0.5
        highlight.OutlineTransparency = 0
        highlight.Parent = parent
        return highlight
    end

    local function GetESPColor(espType)
        if espType == "Monster" then
            return ESP.Settings.MonstersColor
        elseif espType == "Generator" then
            return ESP.Settings.GeneratorsColor
        elseif espType == "Item" then
            return ESP.Settings.ItemsColor
        elseif espType == "FakeElevator" then
            return ESP.Settings.FakeElevatorColor
        end
        return Color3.new(1, 1, 1)
    end

    local function IsTypeVisible(espType)
        if espType == "Monster" then return ESP.Settings.ShowMonsters
        elseif espType == "Generator" then return ESP.Settings.ShowGenerators
        elseif espType == "Item" then return ESP.Settings.ShowItems
        elseif espType == "FakeElevator" then return ESP.Settings.ShowFakeElevator
        end
        return true
    end

    local function CreateESPObject(instance, name, espType)
        local obj = {
            Instance = instance,
            Name = name or instance.Name,
            Type = espType,
            Text = CreateText(),
            Tracer = CreateTracer(),
            Highlight = nil,
            Connection = nil,
        }

        if ESP.Settings.ShowHighlight then
            obj.Highlight = CreateHighlight(instance)
        end

        obj.Connection = RunService.RenderStepped:Connect(function()
            if not ESP.Enabled or not obj.Instance or not obj.Instance.Parent or not IsTypeVisible(obj.Type) then
                obj.Text.Visible = false
                obj.Tracer.Visible = false
                if obj.Highlight then obj.Highlight.Enabled = false end
                return
            end

            local character = GetLocalCharacter()
            local hrp = GetHRP(character)
            if not hrp then
                obj.Text.Visible = false
                obj.Tracer.Visible = false
                return
            end

            local targetPart = obj.Instance:IsA("Model") and (
                obj.Instance:FindFirstChild("HumanoidRootPart") or
                obj.Instance:FindFirstChild("PrimaryPart") or
                obj.Instance:FindFirstChildWhichIsA("BasePart")
            ) or (obj.Instance:IsA("BasePart") and obj.Instance)

            if not targetPart then
                obj.Text.Visible = false
                obj.Tracer.Visible = false
                return
            end

            local targetPos = targetPart.Position
            local screenPos, onScreen = WorldToScreen(targetPos)
            local distance = (hrp.Position - targetPos).Magnitude

            if not onScreen or distance > ESP.Settings.MaxDistance then
                obj.Text.Visible = false
                obj.Tracer.Visible = false
                if obj.Highlight then obj.Highlight.Enabled = false end
                return
            end

            if ESP.Settings.ShowText then
                obj.Text.Position = screenPos - Vector2.new(0, 20)
                obj.Text.Text = string.format("%s\n[%d studs]", obj.Name, math.floor(distance))
                obj.Text.Color = GetESPColor(obj.Type)
                obj.Text.Visible = true
            else
                obj.Text.Visible = false
            end

            if ESP.Settings.ShowTracer then
                local viewportSize = workspace.CurrentCamera.ViewportSize
                obj.Tracer.From = Vector2.new(viewportSize.X / 2, viewportSize.Y)
                obj.Tracer.To = screenPos
                obj.Tracer.Color = GetESPColor(obj.Type)
                obj.Tracer.Visible = true
            else
                obj.Tracer.Visible = false
            end

            if obj.Highlight then
                obj.Highlight.Enabled = ESP.Settings.ShowHighlight
                if ESP.Settings.ShowHighlight then
                    obj.Highlight.FillColor = GetESPColor(obj.Type)
                end
            end
        end)

        return obj
    end

    local function CleanupESPObject(obj)
        if obj.Connection then obj.Connection:Disconnect() end
        if obj.Text then obj.Text:Remove() end
        if obj.Tracer then obj.Tracer:Remove() end
        if obj.Highlight then obj.Highlight:Destroy() end
    end

    local function ClearESP()
        for _, obj in pairs(ESP.Monsters) do CleanupESPObject(obj) end
        ESP.Monsters = {}
        for _, obj in pairs(ESP.Generators) do CleanupESPObject(obj) end
        ESP.Generators = {}
        for _, obj in pairs(ESP.Items) do CleanupESPObject(obj) end
        ESP.Items = {}
        if ESP.FakeElevator then
            CleanupESPObject(ESP.FakeElevator)
            ESP.FakeElevator = nil
        end
    end

    local function ScanFolder(folder, targetTable, espType, nameOverride)
        if not folder then return end
        for _, child in ipairs(folder:GetChildren()) do
            if not targetTable[child] then
                targetTable[child] = CreateESPObject(child, nameOverride or child.Name, espType)
            end
        end
    end

    local function UpdateESP()
        if not ESP.Enabled then
            ClearESP()
            return
        end

        local roomFolder = GetCurrentRoom()
        if not roomFolder then
            ClearESP()
            return
        end

        local monstersFolder = roomFolder:FindFirstChild("Monsters")
        if monstersFolder then
            ScanFolder(monstersFolder, ESP.Monsters, "Monster")
            for instance, obj in pairs(ESP.Monsters) do
                if not instance.Parent then
                    CleanupESPObject(obj)
                    ESP.Monsters[instance] = nil
                end
            end
        end

        local generatorsFolder = roomFolder:FindFirstChild("Generators")
        if generatorsFolder then
            ScanFolder(generatorsFolder, ESP.Generators, "Generator", "Generator")
            for instance, obj in pairs(ESP.Generators) do
                if not instance.Parent then
                    CleanupESPObject(obj)
                    ESP.Generators[instance] = nil
                end
            end
        end

        local itemsFolder = roomFolder:FindFirstChild("Items")
        if itemsFolder then
            ScanFolder(itemsFolder, ESP.Items, "Item")
            for instance, obj in pairs(ESP.Items) do
                if not instance.Parent then
                    CleanupESPObject(obj)
                    ESP.Items[instance] = nil
                end
            end
        end

        local freeArea = roomFolder:FindFirstChild("FreeArea")
        if freeArea then
            local fakeElevator = freeArea:FindFirstChild("FakeElevator")
            if fakeElevator then
                if not ESP.FakeElevator or ESP.FakeElevator.Instance ~= fakeElevator then
                    if ESP.FakeElevator then CleanupESPObject(ESP.FakeElevator) end
                    ESP.FakeElevator = CreateESPObject(fakeElevator, "Fake Elevator", "FakeElevator")
                end
            elseif ESP.FakeElevator then
                CleanupESPObject(ESP.FakeElevator)
                ESP.FakeElevator = nil
            end
        elseif ESP.FakeElevator then
            CleanupESPObject(ESP.FakeElevator)
            ESP.FakeElevator = nil
        end
    end

    local espUpdateConnection = nil
    local roomChangedConnection = nil

    local function StartESP()
        if espUpdateConnection then espUpdateConnection:Disconnect() end
        UpdateESP()
        espUpdateConnection = RunService.RenderStepped:Connect(function()
            UpdateESP()
        end)
        local currentRoom = workspace:FindFirstChild("CurrentRoom")
        if currentRoom then
            roomChangedConnection = currentRoom.ChildAdded:Connect(function()
                ClearESP()
                task.wait(0.5)
                UpdateESP()
            end)
        end
    end

    local function StopESP()
        if espUpdateConnection then
            espUpdateConnection:Disconnect()
            espUpdateConnection = nil
        end
        if roomChangedConnection then
            roomChangedConnection:Disconnect()
            roomChangedConnection = nil
        end
        ClearESP()
    end

    -- Master Toggle
    ESPSection:Toggle({
        Title = "Enable ESP",
        Desc = "Toggle all ESP features",
        Value = false,
        Callback = function(state)
            ESP.Enabled = state
            if state then
                StartESP()
                WindUI:Notify({ Title = "ESP Enabled", Content = "ESP is now active", Duration = 3 })
            else
                StopESP()
                WindUI:Notify({ Title = "ESP Disabled", Content = "ESP is now inactive", Duration = 3 })
            end
        end,
    })

    ESPSection:Space()

    ESPSection:Toggle({
        Title = "ESP Monsters",
        Desc = "Show ESP for monsters",
        Value = true,
        Callback = function(state)
            ESP.Settings.ShowMonsters = state
            if not state then
                for _, obj in pairs(ESP.Monsters) do
                    obj.Text.Visible = false
                    obj.Tracer.Visible = false
                    if obj.Highlight then obj.Highlight.Enabled = false end
                end
            end
        end,
    })

    ESPSection:Space()

    ESPSection:Toggle({
        Title = "ESP Generators",
        Desc = "Show ESP for generators",
        Value = true,
        Callback = function(state)
            ESP.Settings.ShowGenerators = state
            if not state then
                for _, obj in pairs(ESP.Generators) do
                    obj.Text.Visible = false
                    obj.Tracer.Visible = false
                    if obj.Highlight then obj.Highlight.Enabled = false end
                end
            end
        end,
    })

    ESPSection:Space()

    ESPSection:Toggle({
        Title = "ESP Items",
        Desc = "Show ESP for items",
        Value = true,
        Callback = function(state)
            ESP.Settings.ShowItems = state
            if not state then
                for _, obj in pairs(ESP.Items) do
                    obj.Text.Visible = false
                    obj.Tracer.Visible = false
                    if obj.Highlight then obj.Highlight.Enabled = false end
                end
            end
        end,
    })

    ESPSection:Space()

    ESPSection:Toggle({
        Title = "ESP Fake Elevator",
        Desc = "Show ESP for FakeElevator",
        Value = true,
        Callback = function(state)
            ESP.Settings.ShowFakeElevator = state
            if not state and ESP.FakeElevator then
                ESP.FakeElevator.Text.Visible = false
                ESP.FakeElevator.Tracer.Visible = false
                if ESP.FakeElevator.Highlight then ESP.FakeElevator.Highlight.Enabled = false end
            end
        end,
    })

    -- Style Section
    local ESPStyleSection = ESPTab:Section({
        Title = "ESP Style",
        Desc = "Customize ESP appearance",
        Box = true,
        BoxBorder = true,
        Opened = true,
    })

    ESPStyleSection:Toggle({
        Title = "Show Names & Distance",
        Value = true,
        Callback = function(state) ESP.Settings.ShowText = state end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Toggle({
        Title = "Show Tracers",
        Value = true,
        Callback = function(state) ESP.Settings.ShowTracer = state end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Toggle({
        Title = "Show Highlights",
        Value = true,
        Callback = function(state)
            ESP.Settings.ShowHighlight = state
            local all = {}
            for _, o in pairs(ESP.Monsters) do table.insert(all, o) end
            for _, o in pairs(ESP.Generators) do table.insert(all, o) end
            for _, o in pairs(ESP.Items) do table.insert(all, o) end
            if ESP.FakeElevator then table.insert(all, ESP.FakeElevator) end
            for _, o in ipairs(all) do
                if o.Highlight then o.Highlight.Enabled = state end
            end
        end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Text Color",
        Default = Color3.new(1, 1, 1),
        Callback = function(color) ESP.Settings.TextColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Tracer Color",
        Default = Color3.new(1, 1, 1),
        Callback = function(color) ESP.Settings.TracerColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Highlight Color",
        Default = Color3.new(1, 1, 1),
        Callback = function(color)
            ESP.Settings.HighlightColor = color
            local all = {}
            for _, o in pairs(ESP.Monsters) do table.insert(all, o) end
            for _, o in pairs(ESP.Generators) do table.insert(all, o) end
            for _, o in pairs(ESP.Items) do table.insert(all, o) end
            if ESP.FakeElevator then table.insert(all, ESP.FakeElevator) end
            for _, o in ipairs(all) do
                if o.Highlight then o.Highlight.FillColor = color end
            end
        end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Monster Color",
        Default = Color3.fromRGB(255, 0, 0),
        Callback = function(color) ESP.Settings.MonstersColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Generator Color",
        Default = Color3.fromRGB(0, 255, 0),
        Callback = function(color) ESP.Settings.GeneratorsColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Item Color",
        Default = Color3.fromRGB(255, 255, 0),
        Callback = function(color) ESP.Settings.ItemsColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Colorpicker({
        Title = "Fake Elevator Color",
        Default = Color3.fromRGB(255, 0, 255),
        Callback = function(color) ESP.Settings.FakeElevatorColor = color end,
    })

    ESPStyleSection:Space()

    ESPStyleSection:Slider({
        Title = "Max ESP Distance",
        Desc = "Maximum distance to show ESP",
        Step = 10,
        Value = { Min = 100, Max = 10000, Default = 5000 },
        Callback = function(value) ESP.Settings.MaxDistance = value end,
    })

    -- Info Section
    local ESPInfoSection = ESPTab:Section({
        Title = "ESP Info",
        Box = true,
        BoxBorder = true,
        Opened = false,
    })

    local ESPStatusParagraph = ESPInfoSection:Paragraph({
        Title = "Status",
        Desc = "ESP: Disabled\nMonsters: 0\nGenerators: 0\nItems: 0\nFake Elevator: Not Found",
    })

    task.spawn(function()
        while true do
            task.wait(1)
            ESPStatusParagraph:SetDesc(string.format(
                "ESP: %s\nMonsters: %d\nGenerators: %d\nItems: %d\nFake Elevator: %s",
                ESP.Enabled and "Enabled" or "Disabled",
                countTable(ESP.Monsters),
                countTable(ESP.Generators),
                countTable(ESP.Items),
                ESP.FakeElevator and "Found" or "Not Found"
            ))
        end
    end)

    Window.OnDestroy = function()
        StopESP()
    end
end
  Notify()