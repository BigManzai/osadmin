#!/usr/bin/python3
# OpenSim-Commands
# Python 3.6 - 2018 by BigManzai Version  1.0

import configparser
import xmlrpc.client

#def osConfig():
config = configparser.ConfigParser()
config.sections()
config.read('osconfig.ini')
SimulatorAdress = config['DEFAULT']['SimulatorAdress']
ConsoleUser = config['DEFAULT']['ConsoleUser']
ConsolePass = config['DEFAULT']['ConsolePass']
Simulator = xmlrpc.client.Server(SimulatorAdress)
	#return

def osAlert(message):
	alertmessage = "alert " + message
	Simulator.admin_console_command({'password': ConsolePass,'command': alertmessage})
	osAlertInfo = "Send an alert to everyone"
	return
	
def osAlertUser(firstname, lastname, message):
	alertusermessage = "alert-user " + firstname + " " + lastname + " " + message
	Simulator.admin_console_command({'password': ConsolePass,'command': alertusermessage})
	osAlertUserInfo = "Send an alert to a user"
	return
	
def osAppearanceRebake(firstname, lastname):
	AppearanceRebake = "appearance rebake " + firstname + " " + lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': AppearanceRebake})
	osAppearanceRebakeInfo = "Send a request to the user's viewer for it to rebake and reupload its appearance textures."
	return
	
def osAppearanceSend(firstname, lastname):
	appearancesend = "appearance send " + firstname + " " + lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': appearancesend})
	osAppearanceSendInfo = "Send a request to the user's viewer for it to rebake and reupload its appearance textures."
	return
	
def osBackup():
	Simulator.admin_console_command({'password': ConsolePass,'command': "backup"})
	osBackupInfo = "Persist currently unsaved object changes immediately instead of waiting for the normal persistence call."
	return
	
def osbypasspermissions(onoff):
	bypasspermissions = "bypass permissions " + onoff
	Simulator.admin_console_command({'password': ConsolePass,'command': bypasspermissions})
	osbypasspermissionsInfo = "Bypass permission checks true/false"
	return
	
def osChangeRegion(region):
	changeregion = "change region " + region
	Simulator.admin_console_command({'password': ConsolePass,'command': changeregion})
	osChangeRegionInfo = "Change current console region."
	return
	
def osClearImageQueues(firstname, lastname):
	clearimagequeues = "clear image queues " + firstname + " " + lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': clearimagequeues})
	osClearImageQueuesInfo = "Clear the image queues (textures downloaded via UDP) for a particular client."
	return
	
def osCommandScript(script):
	CommandScript = "command-script " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osCommandScriptInfo = "Run a command script from file."
	return

def osConfigSave(path):
	ConfigSave = "config save " + path
	Simulator.admin_console_command({'password': ConsolePass,'command': ConfigSave})
	osConfigSaveInfo = "config save <path> - Save current configuration to a file at the given path"
	return

def osConfigSet(section, key, value):
	ConfigSet = "config set " + section + " " + key + " " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': ConfigSet})
	osConfigSetInfo = "config set <section> <key> <value> - Set a config option.  In most cases this is not useful since changed parameters are not dynamically reloaded.  Neither do changed parameters persist - you will have to change a config file manually and restart."
	return
#osConfigSet(section, key, value)

def osCreateRegion(regionname):
	CreateRegion = "create region " + regionname
	Simulator.admin_console_command({'password': ConsolePass,'command': CreateRegion})
	osCreateRegionInfo = "create region [region name] <region_file.ini> - Create a new region."
	return

def osDebugAttachments(log):
	DebugAttachments = "debug attachments " + log
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugAttachments})
	osDebugAttachmentsInfo = "debug attachments log [0|1] - Turn on attachments debug logging"
	return

def osDebugAttachmentsThrottle(ms):
	DebugAttachmentsThrottle = "debug attachments throttle " + ms
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugAttachmentsThrottle})
	osDebugAttachmentsThrottleInfo = "debug attachments throttle <ms> - Turn on attachments throttling."
	return

def osDebugEq(number):
	DebugEq = "debug eq " + number
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugEq})
	osDebugEqInfo = "debug eq [0|1|2] - Turn on event queue debugging  <= 0 - turns off all event queue logging  >= 1 - turns on event queue setup and outgoing event logging  >= 2 - turns on poll notification"
	return
  
def osDebugGroupsMessagingVerbose(setting):
	DebugGroupsMessagingVerbose = "debug groups messaging verbose " + setting
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugGroupsMessagingVerbose})
	osDebugGroupsMessagingVerboseInfo = "debug groups messaging verbose <true|false> - This setting turns on very verbose groups messaging debugging"
	return

def osDebugGroupsMessaging(setting):
	DebugGroupsMessaging = "debug groups verbose " + setting
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugGroupsMessaging})
	osDebugGroupsMessagingInfo = "debug groups verbose <true|false> - This setting turns on very verbose groups debugging"
	return

def osDebugHttp(level):
	DebugHttp = "debug http " + level
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugHttp})
	osDebugHttpInfo = "debug http <in|out|all> [<level>] - Turn on http request logging."
	return

def osDebugJobengine(level):
	DebugJobengine = "debug jobengine " + level
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugJobengine})
	osDebugJobengineInfo = "debug jobengine <start|stop|status|log> - Start, stop, get status or set logging level of the job engine."
	return

def osDebugPermissions(truefalse):
	DebugPermissions = "debug permissions " + truefalse
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugPermissions})
	osDebugPermissionsInfo = "debug permissions <true/false> - Turn on permissions debugging"
	return

def osDebugSceneSet(param, value):
	DebugSceneSet = "debug scene set " + param + value
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugSceneSet})
	osDebugSceneSetInfo = "debug scene set <param> <value> - Turn on scene debugging options."
	return

def osDebugScriptsLog(itemid, loglevel):
	DebugScriptsLog = "debug scripts log " + itemid + loglevel
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugScriptsLog})
	osDebugScriptsLogInfo = "debug scripts log <item-id> <log-level> - Extra debug logging for a particular script."
	return

def osDebugThreadpoolLevel(level):
	DebugThreadpoolLevel = "debug threadpool level " + level
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugThreadpoolLevel})
	osDebugThreadpoolLevelInfo = "debug threadpool level 0..3 - Turn on logging of activity in the main thread pool."
	return

def osDebugThreadpoolSet(workeriocp, minmax):
	DebugThreadpoolSet = "debug threadpool set " + workeriocp + minmax
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugThreadpoolSet})
	osDebugThreadpoolSetInfo = "debug threadpool set worker|iocp min|max <n> - Set threadpool parameters.  For debug purposes."
	return

def osDebugXengineLog(level):
	DebugXengineLog = "debug xengine log " + level
	Simulator.admin_console_command({'password': ConsolePass,'command': DebugXengineLog})
	osDebugXengineLogInfo = "debug xengine log [<level>] - Turn on detailed xengine debugging."
	return

def osDeleteObjectCreator(osUUID):
	DeleteObjectCreator = "delete object creator " + osUUID
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectCreator})
	osDeleteObjectCreatorInfo = "delete object creator <UUID> - Delete scene objects by creator"
	return

def osDeleteObjectId(UUIDorlocalID):
	DeleteObjectId = "delete object id " + UUIDorlocalID
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectId})
	osDeleteObjectIdInfo = "delete object id <UUID-or-localID> - Delete a scene object by uuid or localID"
	return

def osDeleteObjectName(name):
	DeleteObjectName = "delete object name " + name
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectName})
	osDeleteObjectNameInfo = "delete object name [--regex] <name> - Delete a scene object by name."
	return

def osDeleteObjectOutside():
	DeleteObjectOutside = "delete object outside "
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectOutside})
	osDeleteObjectOutsideInfo = "delete object outside - Delete all scene objects outside region boundaries"
	return

def osDeleteObjectOwner(ownerUUID):
	DeleteObjectOwner = "delete object owner " + ownerUUID
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectOwner})
	osDeleteObjectOwnerInfo = "delete object owner <UUID> - Delete scene objects by owner"
	return

def osDeleteObjectPos(startx, starty, startz, endx, endy, endz):
	DeleteObjectPos = "delete object pos " + startx + starty + startz + endx + endy + endz
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteObjectPos})
	osDeleteObjectPosInfo = "delete object pos <start x, start y , start z> <end x, end y, end z> - Delete scene objects within the given volume."
	return

def osDeleteRegion(name):
	DeleteRegion = "delete-region " + name
	Simulator.admin_console_command({'password': ConsolePass,'command': DeleteRegion})
	osDeleteRegionInfo = "delete-region <name> - Delete a region from disk"
	return

def osDumpAsset(assetid):
	DumpAsset = "dump asset " + assetid
	Simulator.admin_console_command({'password': ConsolePass,'command': DumpAsset})
	osDumpAssetInfo = "dump asset <id> - Dump an asset"
	return

def osDumpObjectId(UUIDlocalID):
	DumpObjectId = "dump object id " + UUIDlocalID
	Simulator.admin_console_command({'password': ConsolePass,'command': DumpObjectId})
	osDumpObjectIdInfo = "dump object id <UUID-or-localID> - Dump the formatted serialization of the given object to the file <UUID>.xml"
	return

def osEditScale(name, x, y, z):
	EditScale = "edit scale " + name + x + y + z
	Simulator.admin_console_command({'password': ConsolePass,'command': EditScale})
	osEditScaleInfo = "edit scale <name> <x> <y> <z> - Change the scale of a named prim"
	return

def osEstateCreate(ownerUUID, estatename):
	EstateCreate = "estate create " + ownerUUID + estatename
	Simulator.admin_console_command({'password': ConsolePass,'command': EstateCreate})
	osEstateCreateInfo = "estate create <owner UUID> <estate name> - Creates a new estate with the specified name, owned by the specified user. Estate name must be unique."
	return

def osCommandScript(script):
	CommandScript = "command-script " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osCommandScriptInfo = "estate link region <estate ID> <region ID> - Attaches the specified region to the specified estate."
	return

def osEstateSetName(estateid, newname):
	EstateSetName = "estate set name " + estateid + newname
	Simulator.admin_console_command({'password': ConsolePass,'command': EstateSetName})
	osEstateSetNameInfo = "estate set name <estate-id> <new name> - Sets the name of the specified estate to the specified value. New name must be unique."
	return

def osEstateSetOwner(estateid, UUID, Firstname, Lastname):
	EstateSetOwner = "estate set owner " + estateid + UUID + Firstname + Lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': EstateSetOwner})
	osEstateSetOwnerInfo = "estate set owner <estate-id>[ <UUID> | <Firstname> <Lastname> ] - Sets the owner of the specified estate to the specified UUID or user."
	return

def osExportMap(path):
	ExportMap = "export-map " + path
	Simulator.admin_console_command({'password': ConsolePass,'command': ExportMap})
	osExportMapInfo = "export-map [<path>] - Save an image of the world map"
	return

def osFcacheAssets():
	FcacheAssets = "fcache assets"
	Simulator.admin_console_command({'password': ConsolePass,'command': FcacheAssets})
	osFcacheAssetsInfo = "fcache assets - Attempt a deep scan and cache of all assets in all scenes"
	return

def osFcacheClear(file, memory):
	FcacheClear = "fcache clear " + file + memory
	Simulator.admin_console_command({'password': ConsolePass,'command': FcacheClear})
	osFcacheClearInfo = "fcache clear [file] [memory] - Remove all assets in the cache.  If file or memory is specified then only this cache is cleared."
	return

def osFcacheExpire(datetime):
	FcacheExpire = "fcache expire " + datetime
	Simulator.admin_console_command({'password': ConsolePass,'command': FcacheExpire})
	osFcacheExpireInfo = "fcache expire <datetime> - Purge cached assets older then the specified date/time"
	return

def osForceGc():
	ForceGc = "force gc"
	Simulator.admin_console_command({'password': ConsolePass,'command': ForceGc})
	osForceGcInfo = "force gc - Manually invoke runtime garbage collection.  For debugging purposes"
	return

def osForcePermissions(truefalse):
	ForcePermissions = "force permissions " + truefalse
	Simulator.admin_console_command({'password': ConsolePass,'command': ForcePermissions})
	osForcePermissionsInfo = "force permissions <true / false> - Force permissions on or off"
	return

def osForceUpdate():
	ForceUpdate = "force update"
	Simulator.admin_console_command({'password': ConsolePass,'command': ForceUpdate})
	osForceUpdateInfo = "force update - Force the update of all objects on clients"
	return

def osGenerateMap():
	GenerateMap = "generate map"
	Simulator.admin_console_command({'password': ConsolePass,'command': GenerateMap})
	osGenerateMapInfo = "generate map - Generates and stores a new maptile."
	return

def osJ2kDecode(j2kID):
	J2kDecode = "j2k decode " + j2kID
	Simulator.admin_console_command({'password': ConsolePass,'command': J2kDecode})
	osJ2kDecodeInfo = "j2k decode <ID> - Do JPEG2000 decoding of an asset."
	return

def osKickUser(firstname, lastname, message):
	KickUser = "kick user " + firstname + lastname + message
	Simulator.admin_console_command({'password': ConsolePass,'command': KickUser})
	osKickUserInfo = "kick user <first> <last> [--force] [message] - Kick a user off the simulator"
	return

def osLandClear():
	LandClear = "land clear"
	Simulator.admin_console_command({'password': ConsolePass,'command': LandClear})
	osLandClearInfo = "land clear - Clear all the parcels from the region."
	return

def osLinkMapping(x, y):
	LinkMapping = "link-mapping " + x + y
	Simulator.admin_console_command({'password': ConsolePass,'command': LinkMapping})
	osLinkMappingInfo = "link-mapping [<x> <y>] - Set local coordinate to map HG regions to"
	return

def osLinkRegion(Xloc, Yloc):
	LinkRegion = "link-region " + Xloc + Yloc
	Simulator.admin_console_command({'password': ConsolePass,'command': LinkRegion})
	osLinkRegionInfo = "link-region <Xloc> <Yloc> <ServerURI> [<RemoteRegionName>] - Link a HyperGrid Region. Examples for <ServerURI>: http://grid.net:8002/ or http://example.org/path/foo.php"
	return

def osLoadIar(firstname, lastname, inventorypath, password, IARpath):
	LoadIar = "load iar " + firstname + lastname + inventorypath + password + IARpath
	Simulator.admin_console_command({'password': ConsolePass,'command': LoadIar})
	osLoadIarInfo = "load iar [-m|--merge] <first> <last> <inventory path> <password> [<IAR path>] - Load user inventory archive (IAR)."
	return

def osLoadOar(loadoaroption):
	LoadOar = "load oar " + loadoaroption
	Simulator.admin_console_command({'password': ConsolePass,'command': LoadOar})
	osLoadOarInfo = "load oar [-m|--merge] [-s|--skip-assets] [--default-user UserName] [--force-terrain] [--force-parcels] [--no-objects] [--rotation degrees] [--bounding-origin <x,y,z>] [--bounding-size <x,y,z>] [--displacement <x,y,z>] [-d|--debug] [<OAR path>] - Load a region's data from an OAR archive."
	return

def osLoadXml(loadxmloption):
	LoadXml = "load xml " + loadxmloption
	Simulator.admin_console_command({'password': ConsolePass,'command': LoadXml})
	osLoadXmlInfo = "load xml [<file name> [-newUID [<x> <y> <z>]]] - Load a region's data from XML format"
	return

def osLoadXml2(filename):
	LoadXml2 = "load xml2 " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': LoadXml2})
	osLoadXml2Info = "load xml2 [<file name>] - Load a region's data from XML2 format"
	return

def osLoginDisable():
	LoginDisable = "login disable"
	Simulator.admin_console_command({'password': ConsolePass,'command': LoginDisable})
	osLoginDisableInfo = "login disable - Disable simulator logins"
	return

def osLoginEnable():
	LoginEnable = "login enable"
	Simulator.admin_console_command({'password': ConsolePass,'command': LoginEnable})
	osLoginEnableInfo = "login enable - Enable simulator logins"
	return

def osPhysicsSet(param):
	PhysicsSet = "physics set " + param
	Simulator.admin_console_command({'password': ConsolePass,'command': PhysicsSet})
	osPhysicsSetInfo = "physics set <param> [<value>|TRUE|FALSE] [localID|ALL] - Set physics parameter from currently selected region"
	return

def osRegionRestartAbort(message):
	RegionRestartAbort = "region restart abort " + message
	Simulator.admin_console_command({'password': ConsolePass,'command': RegionRestartAbort})
	osRegionRestartAbortInfo = "region restart abort [<message>] - Abort a region restart"
	return
	
def osRegionRestartBluebox(message):
	RegionRestartBluebox = "region restart bluebox " + message
	Simulator.admin_console_command({'password': ConsolePass,'command': RegionRestartBluebox})
	osRegionRestartBlueboxInfo = "region restart bluebox <message> <delta seconds>+ - Schedule a region restart"
	return	

def osRegionRestartNotice(message, seconds):
	RegionRestartNotice = "region restart notice " + message + seconds
	Simulator.admin_console_command({'password': ConsolePass,'command': RegionRestartNotice})
	osRegionRestartNoticeInfo = "region restart notice <message> <delta seconds>+ - Schedule a region restart"
	return

def osRemoveRegion(name):
	RemoveRegion = "remove-region " + name
	Simulator.admin_console_command({'password': ConsolePass,'command': RemoveRegion})
	osRemoveRegionInfo = "remove-region <name> - Remove a region from this simulator"
	return

def osResetUserCache():
	ResetUserCache = "reset user cache"
	Simulator.admin_console_command({'password': ConsolePass,'command': ResetUserCache})
	osResetUserCacheInfo = "reset user cache - reset user cache to allow changed settings to be applied"
	return

def osRotateScene(degrees, centerX, centerY):
	RotateScene = "rotate scene " + degrees + centerX + centerY
	Simulator.admin_console_command({'password': ConsolePass,'command': RotateScene})
	osRotateSceneInfo = "rotate scene <degrees> [centerX, centerY] - Rotates all scene objects around centerX, centerY (default 128, 128) (please back up your region before using)"
	return

def osSaveIar(iarparameters):
	SaveIar = "save iar " + iarparameters
	Simulator.admin_console_command({'password': ConsolePass,'command': SaveIar})
	osSaveIarInfo = "save iar [-h|--home=<url>] [--noassets] <first> <last> <inventory path> <password> [<IAR path>] [-c|--creators] [-e|--exclude=<name/uuid>] [-f|--excludefolder=<foldername/uuid>] [-v|--verbose] - Save user inventory archive (IAR)."
	return

def osSaveOar(oarparameters):
	SaveOar = "save oar " + oarparameters
	Simulator.admin_console_command({'password': ConsolePass,'command': SaveOar})
	osSaveOarInfo = "save oar [-h|--home=<url>] [--noassets] [--publish] [--perm=<permissions>] [--all] [<OAR path>] - Save a region's data to an OAR archive."
	return

def osSavePrimsXml2(primname, filename):
	SavePrimsXml2 = "save prims xml2 " + primname + filename
	Simulator.admin_console_command({'password': ConsolePass,'command': SavePrimsXml2})
	osSavePrimsXml2Info = "save prims xml2 [<prim name> <file name>] - Save named prim to XML2"
	return

def osSaveXml(xmlfilename):
	SaveXml = "save xml " + xmlfilename
	Simulator.admin_console_command({'password': ConsolePass,'command': SaveXml})
	osSaveXmlInfo = "save xml [<file name>] - Save a region's data in XML format"
	return

def osSaveXml2(xml2filename):
	SaveXml2 = "save xml2 " + xml2filename
	Simulator.admin_console_command({'password': ConsolePass,'command': SaveXml2})
	osSaveXml2Info = "save xml2 [<filename>] - Save a region's data in XML2 format"
	return

def osScaleScene(factor):
	ScaleScene = "scale scene " + factor
	Simulator.admin_console_command({'password': ConsolePass,'command': ScaleScene})
	osScaleSceneInfo = "scale scene <factor> - Scales the scene objects (please back up your region before using)"
	return

def osScriptsResume(scriptitemuuid):
	ScriptsResume = "scripts resume " + scriptitemuuid
	Simulator.admin_console_command({'password': ConsolePass,'command': ScriptsResume})
	osScriptsResumeInfo = "scripts resume [<script-item-uuid>+] - Resumes all suspended scripts"
	return

def osScriptsStart(scriptitemuuid):
	ScriptsStart = "scripts start " + scriptitemuuid
	Simulator.admin_console_command({'password': ConsolePass,'command': ScriptsStart})
	osScriptsStartInfo = "scripts start [<script-item-uuid>+] - Starts all stopped scripts"
	return

def osScriptsStop(scriptitemuuid):
	ScriptsStop = "scripts stop " + scriptitemuuid
	Simulator.admin_console_command({'password': ConsolePass,'command': ScriptsStop})
	osScriptsStopInfo = "scripts stop [<script-item-uuid>+] - Stops all running scripts"
	return

def osScriptsSuspend(scriptitemuuid):
	ScriptsSuspendt = "scripts suspend " + scriptitemuuid
	Simulator.admin_console_command({'password': ConsolePass,'command': ScriptsSuspend})
	osScriptsSuspendInfo = "scripts suspend [<script-item-uuid>+] - Suspends all running scripts"
	return

def osSetLogLevel(level):
	SetLogLevel = "set log level " + level
	Simulator.admin_console_command({'password': ConsolePass,'command': SetLogLevel})
	osSetLogLevelInfo = "set log level <level> - Set the console logging level for this session."
	return

def osSetTerrainHeights(parameters):
	SetTerrainHeights = "set terrain heights " + parameters
	Simulator.admin_console_command({'password': ConsolePass,'command': SetTerrainHeights})
	osSetTerrainHeightsInfo = "set terrain heights <corner> <min> <max> [<x>] [<y>] - Sets the terrain texture heights on corner #<corner> to <min>/<max>, if <x> or <y> are specified, it will only set it on regions with a matching coordinate. Specify -1 in <x> or <y> to wildcard that coordinate. Corner # SW = 0, NW = 1, SE = 2, NE = 3, all corners = -1."
	return

def osSetTerrainTexture(parameters):
	SetTerrainTexture = "set terrain texture " + parameters
	Simulator.admin_console_command({'password': ConsolePass,'command': SetTerrainTexture})
	osSetTerrainTextureInfo = "set terrain texture <number> <uuid> [<x>] [<y>] - Sets the terrain <number> to <uuid>, if <x> or <y> are specified, it will only set it on regions with a matching coordinate. Specify -1 in <x> or <y> to wildcard that coordinate."
	return

def osSetWaterHeight(heightxy):
	SetWaterHeight = "set water height " + heightxy
	Simulator.admin_console_command({'password': ConsolePass,'command': SetWaterHeight})
	osSetWaterHeightInfo = "set water height <height> [<x>] [<y>] - Sets the water height in meters.  If <x> and <y> are specified, it will only set it on regions with a matching coordinate. Specify -1 in <x> or <y> to wildcard that coordinate."
	return

def osShutdown(script):
	Shutdown = "shutdown"
	Simulator.admin_console_command({'password': ConsolePass,'command': Shutdown})
	osShutdownInfo = "shutdown - Quit the application"
	return

def osSitUserName(firstname, lastname):
	SitUserName = "sit user name " + firstname + lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': SitUserName})
	osSitUserNameInfo = "sit user name [--regex] <first-name> <last-name> - Sit the named user on an unoccupied object with a sit target."
	return

def osStandUserName(firstname, lastname):
	StandUserName = "stand user name " + firstname + lastname
	Simulator.admin_console_command({'password': ConsolePass,'command': StandUserName})
	osStandUserNameInfo = "stand user name [--regex] <first-name> <last-name> - Stand the named user."
	return

def osStatsRecord(startstop):
	StatsRecord = "stats record " + startstop
	Simulator.admin_console_command({'password': ConsolePass,'command': StatsRecord})
	osStatsRecordInfo = "stats record start|stop - Control whether stats are being regularly recorded to a separate file."
	return

def osStatsSave(path):
	StatsSave = "stats save " + path
	Simulator.admin_console_command({'password': ConsolePass,'command': StatsSave})
	osStatsSaveInfo = "stats save <path> - Save stats snapshot to a file.  If the file already exists, then the report is appended."
	return

def osSunCurrentTime(value):
	SunCurrentTime = "sun current_time " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': SunCurrentTime})
	osSunCurrentTimeInfo = "sun current_time [<value>] - time in seconds of the simulator"
	return

def osSunDayLength(value):
	SunDayLength = "sun day_length " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': SunDayLength})
	osSunDayLengthInfo = "sun day_length [<value>] - number of hours to a day"
	return

def osSunDayNightOffset(value):
	SunDayNightOffset = "sun day_night_offset " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': SunDayNightOffset})
	osSunDayNightOffsetInfo = "sun day_night_offset [<value>] - induces a horizon shift"
	return

def osSunDayTimeSunHourScale(value):
	CommandScript = "sun day_time_sun_hour_scale " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osCommandScriptInfo = "sun day_time_sun_hour_scale [<value>] - scales day light vs nite hours to change day/night ratio"
	return

def osSunUpdateInterval(value):
	SunUpdateInterval = "sun update_interval " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': SunUpdateInterval})
	osSunUpdateIntervalInfo = "sun update_interval [<value>] - how often to update the sun's position in frames"
	return

def osSunYearLength(value):
	SunYearLength = "sun year_length " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': SunYearLength})
	osSunYearLengthInfo = "sun year_length [<value>] - number of days to a year"
	return

def osTeleportUser(firstname, lastname, destination):
	TeleportUser = "teleport user " + firstname + lastname + destination
	Simulator.admin_console_command({'password': ConsolePass,'command': TeleportUser})
	osTeleportUserInfo = "teleport user <first-name> <last-name> <destination> - Teleport a user in this simulator to the given destination"
	return

def osTerrainBake():
	TerrainBake = "terrain bake"
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainBake})
	osTerrainBakeInfo = "terrain bake -"
	return

def osTerrainEffect(name):
	TerrainEffect = "terrain effect " + name
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainEffect})
	osTerrainEffectInfo = "terrain effect <name> "
	return

def osTerrainElevate(amount):
	TerrainElevate = "terrain elevate " + amount
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainElevate})
	osTerrainElevateInfo = "terrain elevate <amount> -"
	return

def osTerrainFill(value):
	TerrainFill = "terrain fill " + value
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainFill})
	osTerrainFillInfo = "terrain fill <value> -"
	return

def osTerrainFlip(direction):
	TerrainFlip = "terrain flip " + direction
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainFlip})
	osTerrainFlipInfo = "terrain flip <direction> -"
	return

def osTerrainLoad(script):
	TerrainLoad = "terrain load " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainLoad})
	osTerrainLoadInfo = "terrain load <filename> -"
	return

def osTerrainLoadTile(script):
	CommandScript = "terrain load-tile " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osCommandScriptInfo = "terrain load-tile <filename> <file width> <file height> <minimum X tile> <minimum Y tile> -"
	return

def osTerrainLower(amount):
	TerrainLower = "terrain lower " + amount
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainLower})
	osTerrainLowerInfo = "terrain lower <amount> -"
	return

def osTerrainMax(max):
	TerrainMax = "terrain max " + max
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainMax})
	osTerrainMaxInfo = "terrain max <min> -"
	return

def osTerrainMin(min):
	TerrainMin = "terrain min " + min
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainMin})
	osTerrainMinInfo = "terrain min <min> -"
	return

def osTerrainModify(operation, value, area, taper):
	TerrainModify = "terrain modify " + operation + value + area + taper
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainModify})
	osTerrainModifyInfo = "terrain modify <operation> <value> [<area>] [<taper>] - Modifies the terrain as instructed."
	return
 
def osTerrainMultiply(tmvalue):
	TerrainMultiply = "terrain multiply " + tmvalue
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainMultiply})
	osTerrainMultiplyInfo = "terrain multiply <value> - Multiplies the heightmap by the value specified."
	return

def osTerrainNewbrushes(Enabled):
	TerrainNewbrushes = "terrain newbrushes " + Enabled
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainNewbrushes})
	osTerrainNewbrushesInfo = "terrain newbrushes <Enabled?> - Enables experimental brushes which replace the standard terrain brushes."
	return

def osTerrainRescale(min, max):
	TerrainRescale = "terrain rescale " + min + max
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainRescale})
	osTerrainRescaleInfo = "terrain rescale <min> <max> - Rescales the current terrain to fit between the given min and max heights."
	return

def osTerrainRevert():
	TerrainRevert = "terrain revert "
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainRevert})
	osTerrainRevertInfo = "terrain revert - Loads the baked map terrain into the regions heightmap. "
	return

def osTerrainSave(filename):
	TerrainSave = "terrain save " + filename
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainSave})
	osTerrainSaveInfo = "terrain save <filename> - Saves the current heightmap to a specified file."
	return

def osTerrainSaveTile(filename, filewidth, fileheight, minimumXtile, minimumYtile):
	TerrainSaveTile = "terrain save-tile " + filename + filewidth + fileheight + minimumXtile + minimumYtile
	Simulator.admin_console_command({'password': ConsolePass,'command': TerrainSaveTile})
	osTerrainSaveTileInfo = "terrain save-tile <filename> <file width> <file height> <minimum X tile> <minimum Y tile> - translate scene xOffset yOffset zOffset - translates the scene objects (please back up your region before using)"
	return
	
def osTreeActive():
	TreeActive = "tree active"
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeActive})
	osTreeActiveInfo = "tree active - Change activity state for the trees module "
	return

def osTreeFreeze():
	TreeFreeze = "tree freeze"
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeFreeze})
	osTreeFreezeInfo = "tree freeze - Freeze/Unfreeze activity for a defined copse "
	return

def osTreeLoad(xmlfile):
	TreeLoad = "tree load " + xmlfile
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeLoad})
	osTreeLoadInfo = "tree load - Load a copse definition from an xml file "
	return

def osTreePlant():
	TreePlant = "tree plant"
	Simulator.admin_console_command({'password': ConsolePass,'command': TreePlant})
	osTreePlantInfo = "tree plant - Start the planting on a copse "
	return

def osTreeRate(mSec):
	TreeRate = "tree rate " + mSec
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeRate})
	osTreeRateInfo = "tree rate - Reset the tree update rate (mSec) "
	return

def osTreeReload():
	TreeReload = "tree reload"
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeReload})
	osTreeReloadInfo = "tree reload - Reload copse definitions from the in-scene trees "
	return

def osTreeRemove():
	TreeRemove = "tree remove"
	Simulator.admin_console_command({'password': ConsolePass,'command': TreeRemove})
	osTreeRemoveInfo = "tree remove - Remove a copse definition and all its in-scene trees "
	return

def osUnlinkRegion(localname):
	CommandScript = "unlink-region " + localname
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osUnlinkRegionInfo = "unlink-region <local name> - Unlink a hypergrid region"
	return

def osVivoxDebug(onoff):
	VivoxDebug = "vivox debug " + script
	Simulator.admin_console_command({'password': ConsolePass,'command': VivoxDebug})
	osVivoxDebugInfo = "vivox debug <on>|<off> - Set vivox debugging"
	return

def osWindlightDisable():
	CommandScript = "windlight disable "
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osWindlightDisableInfo = "windlight disable - Disable the windlight plugin"
	return

def osWindlightEnable():
	CommandScript = "windlight enable "
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osWindlightEnableInfo = "windlight enable - Enable the windlight plugin"
	return

def osWindlightLoad():
	CommandScript = "windlight load "
	Simulator.admin_console_command({'password': ConsolePass,'command': CommandScript})
	osWindlightLoadInfo = "windlight load - Load windlight profile from the database and broadcast"
	return