# -*- coding: utf-8 -*-
"""Adds the v0.5.12 keys to both hjson files in place (run on the device, in Localization/)."""
import sys

T = '\t'


def block(name, body):
    return body


ITEMS = {
    'ko': '''	Mk19Launcher: {
		DisplayName: Mk19 유탄발사기 (노획)
		Tooltip:
			\'\'\'
			40mm 고폭 유탄을 포물선으로 쏜다
			떨어진 자리에서 터지고, 발판 위에서도 터진다
			탄약이 필요 없다
			"탄띠째 뜯어 왔다. 탄띠는 끝나지 않는다. 누가 채워 넣는지는 아무도 모른다."
			\'\'\'
	}
	M230ChainGun: {
		DisplayName: M230 체인건 (노획)
		Tooltip:
			\'\'\'
			총알을 30mm 고폭 이중목적탄으로 바꿔 쏜다
			맞은 자리에서 작게 한 번 더 터진다
			25% 확률로 탄을 아낀다
			"포탑에서 잘라 내고 손잡이를 테이프로 감았다. 전원은 어디서 들어오는 걸까."
			\'\'\'
	}
	GrayEagleTerminal: {
		DisplayName: 그레이 이글 지상통제 단말기
		Tooltip:
			\'\'\'
			실물 크기 MQ-1C 그레이 이글을 불러 함께 싸운다
			적 위를 선회하다가 레이저로 조준하고 헬파이어를 떨군다
			소환수 칸을 2칸 쓴다
			"로그인 화면의 소속 칸이 비어 있다. 그래도 링크는 붙는다."
			\'\'\'
	}
	GuardianHelmet: {
		DisplayName: IHADSS 조종사 헬멧
		Tooltip:
			\'\'\'
			사용하면 CH-47 치누크가 AH-64E 가디언을 실어 온다
			처음 받을 때는 정비반이 내려서 메인 로터를 달아 준다
			세워 둔 기체 가까이에서 사용하거나 기체를 우클릭하면 탑승한다
			멀리 세워 뒀다면 치누크가 다시 실어 온다
			탈것 키나 버프 아이콘으로 내린다
			좌클릭: 30mm 기관포   우클릭: 커서가 잡은 표적에 스파이크 NLOS
			"모노클이 아직 기체에 조준돼 있다. 기체는 너를 조종사로 기억한다."
			\'\'\'
	}
	GuardianSummon: {
		DisplayName: MUM-T 데이터링크 단말기
		Tooltip:
			\'\'\'
			무인기 데이터링크에 접속하면 AH-64E 가디언 편대가 신호를 역추적해 온다
			AH-64D 아파치를 처치한 뒤에 사용할 수 있다
			\'\'\'
	}
''',
    'en': '''	Mk19Launcher: {
		DisplayName: Salvaged Mk19 Grenade Launcher
		Tooltip:
			\'\'\'
			Lobs 40mm HEDP grenades on an arc
			Bursts where it lands, platforms included
			Needs no ammo
			"You tore it off with the belt still in. The belt never runs out, and nobody knows who keeps feeding it."
			\'\'\'
	}
	M230ChainGun: {
		DisplayName: Salvaged M230 Chain Gun
		Tooltip:
			\'\'\'
			Turns bullets into 30mm HEDP rounds
			Each round bursts again where it hits
			25% chance not to consume ammo
			"Cut off the turret, grip taped on. Where the power comes from is anyone's guess."
			\'\'\'
	}
	GrayEagleTerminal: {
		DisplayName: Gray Eagle Ground Control Terminal
		Tooltip:
			\'\'\'
			Calls a full-size MQ-1C Gray Eagle to fight with you
			It loiters over the enemy, lases a target and drops a Hellfire
			Uses 2 minion slots
			"The unit field on the login screen is blank. The link comes up anyway."
			\'\'\'
	}
	GuardianHelmet: {
		DisplayName: IHADSS Flight Helmet
		Tooltip:
			\'\'\'
			Use to have a CH-47 Chinook fly your AH-64E Guardian in
			The first time, the ground crew comes out and fits the main rotor
			Use it near the parked aircraft, or right-click the aircraft, to climb in
			If it is parked far away, the Chinook brings it over again
			Get out with the mount key or the buff icon
			Left click: 30mm gun   Right click: Spike NLOS at the target under the cursor
			"The monocle is still boresighted to the aircraft. The aircraft remembers you as its pilot."
			\'\'\'
	}
	GuardianSummon: {
		DisplayName: MUM-T Datalink Terminal
		Tooltip:
			\'\'\'
			Logging into the drones' data link gets the AH-64E Guardian flight to trace the signal back to you
			Usable after the AH-64D Apache has been defeated
			\'\'\'
	}
''',
}

BUFFS = {
    'ko': '''	GrayEagleBuff: {
		DisplayName: MQ-1C 그레이 이글
		Description: 그레이 이글이 머리 위를 선회한다
	}
	GuardianMountBuff: {
		DisplayName: AH-64E 가디언
		Description: 가디언을 조종하고 있다. 누르면 내린다
	}
''',
    'en': '''	GrayEagleBuff: {
		DisplayName: MQ-1C Gray Eagle
		Description: A Gray Eagle is circling overhead
	}
	GuardianMountBuff: {
		DisplayName: AH-64E Guardian
		Description: You are flying the Guardian. Click to get out
	}
''',
}

PROJ = {
    'ko': [('Mk19Round', '40mm 유탄'), ('M230Round', '30mm 고폭탄'), ('PilotRound', '30mm 고폭탄'), ('Mk19Blast', '폭발'),
           ('M230Blast', '폭발'), ('PilotGunBlast', '폭발'), ('PilotSpikeBlast', '폭발'), ('PilotSpike', '스파이크 NLOS'),
           ('GrayEagleMinion', 'MQ-1C 그레이 이글'), ('GuardianAirframe', 'AH-64E 가디언')],
    'en': [('Mk19Round', '40mm Grenade'), ('M230Round', '30mm HEDP Round'), ('PilotRound', '30mm HEDP Round'), ('Mk19Blast', 'Explosion'),
           ('M230Blast', 'Explosion'), ('PilotGunBlast', 'Explosion'), ('PilotSpikeBlast', 'Explosion'), ('PilotSpike', 'Spike NLOS'),
           ('GrayEagleMinion', 'MQ-1C Gray Eagle'), ('GuardianAirframe', 'AH-64E Guardian')],
}

RADIO = '''	HaulerInbound: "[Radio] Hauler Two-Six, one Guardian on the hook, blades in the back. Inbound to your LZ."
	HaulerDown: "[Radio] Load's on the deck. Coming back around to drop the crew."
	HaulerDownSling: "[Radio] Load's on the deck. Hauler Two-Six, clear."
	HaulerCrew: "[Radio] Ramp's down. Crew chief, get those blades on."
	HaulerBlades: "[Radio] Blades on, pins in, torqued. She's all yours."
	HaulerClear: "[Radio] Hauler Two-Six, lifting. Good hunting."
	HaulerSling: "[Radio] Hauler Two-Six, copy. Picking up your bird, stand by."
	HaulerNoLZ: "[Radio] Hauler Two-Six, negative LZ. Need flat ground and open sky."
	HaulerBusy: "[Radio] Hauler Two-Six, already on it. Stand by."
'''

BESTIARY_ADD = {
    'ko': {
        'HumveeBoss': ' 국가훈련센터에서 야간 훈련을 뛰다가 정체불명의 신호에 휩쓸려 온 첫 부대. 대거 투-원은 아직도 이게 훈련이라고 믿는다.',
        'ApacheBoss': ' 원-원의 피아식별기는 너에게서 끝내 응답을 받지 못했다. 그때부터 너는 교전 규칙상 적이다.',
        'ApacheGuardian': ' 데이터링크로 묶인 셋 중 누구도 명령이 어디서 오는지 묻지 않는다. 인증 코드가 맞으니까.',
    },
    'en': {
        'HumveeBoss': ' The first unit pulled through by the signal, in the middle of a night rotation at the National Training Center. Dagger Two-One still thinks this is the exercise.',
        'ApacheBoss': " One-One's IFF never got an answer out of you. Under the rules of engagement, that makes you hostile.",
        'ApacheGuardian': ' None of the three on the data link asks where the tasking comes from. The authentication codes check out.',
    },
}


def section_end(s, name):
    start = s.index('\n' + name + ': {') + 1
    end = s.index('\n}', start)
    return end


def main(lang, path):
    s = open(path, encoding='utf-8').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    s = s.replace('\r\n', '\n')
    if 'Mk19Launcher' in s:
        print('already patched', path)
        return
    e = section_end(s, 'Items')
    s = s[:e] + '\n' + ITEMS[lang].rstrip('\n') + s[e:]
    e = section_end(s, 'Buffs')
    s = s[:e] + '\n' + BUFFS[lang].rstrip('\n') + s[e:]
    e = section_end(s, 'Projectiles')
    add = '\n'.join('\t%s: {\n\t\tDisplayName: %s\n\t}' % kv for kv in PROJ[lang])
    s = s[:e] + '\n' + add + s[e:]
    e = section_end(s, 'Radio')
    s = s[:e] + '\n' + RADIO.rstrip('\n') + s[e:]
    for key, extra in BESTIARY_ADD[lang].items():
        i = s.index('\n\t' + key + ': ', s.index('\nBestiary: {'))
        j = s.index('\n', i + 1)
        s = s[:j] + extra + s[j:]
    open(path, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
    print('ok', path)


if __name__ == '__main__':
    main('ko', 'ko-KR_Mods.ModernArsenal.hjson')
    main('en', 'en-US_Mods.ModernArsenal.hjson')
