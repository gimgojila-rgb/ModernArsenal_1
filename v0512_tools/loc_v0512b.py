# -*- coding: utf-8 -*-
"""v0.5.12 part 2: the recovered-record lore items (run on the device, in Localization/)."""

KO = """	LoreHint: "Shift를 누르고 있으면 기록을 읽는다"
	LoreHumvee: {
		DisplayName: "회수 기록: 대거 투-원 순찰일지"
		Tooltip: 불탄 험비 운전석에서 나온 방수 수첩
		LoreText:
			\'\'\'
			[D+0 0213Z] 국가훈련센터 야간 순환 3일 차. 전 무전망에 이상한 반송파가 떴다. 통신병 말로는 노래 같단다.
			[D+0 0214Z] 사막이 없어졌다. 숲이다. GPS 위성은 0개. 지도에 없는 지형이다.
			[D+0 0300Z] 중대망이 끊겼다. 부르면 아무도 대답하지 않는다. 대신 인증 코드가 맞는 임무 지시가 계속 들어온다.
			[D+1 0540Z] 전방에 식별 불가 인원 1명. 피아식별 응답 없음. 교전 규칙에 따라 적대로 분류했다.
			[D+1 0712Z] 초록색 젤리 같은 게 차에 달라붙었다. 사수가 M2로 쐈다. 애들한테 훈련 아니라고 말해야 하는데, 나도 모르겠다.
			[D+3 1900Z] 탄띠를 세 번 갈았는데 탄약통은 아직 가득하다. 아무도 이 얘기를 꺼내지 않는다.
			[D+4 ----Z] 치누크 호러 투-식스가 떴다. 우리를 데리러 온 건지 물었더니 인증 코드만 불러 주고 끊었다.
			(마지막 장, 다른 필적) 대거 투-원, 접촉. 목표 식별 불가. 교전한다.
			\'\'\'
	}
	LoreApache: {
		DisplayName: "회수 기록: 원-원 조종실 음성기록"
		Tooltip: 잔해에서 건진 비행기록장치를 판독한 녹취록
		LoreText:
			\'\'\'
			(CVR 판독. 호출부호 원-원. 기록장치 타임스탬프 전부 훈련 당일 00:00:00Z)
			사수: 레이더에 표적 하나. IFF 질의한다.
			조종사: 응답은?
			사수: 없어. 모드 5도, 모드 4도 없어.
			조종사: 그럼 규칙대로다. 원-원, 교전.
			(12초 공백)
			사수: 방금 달 봤어? 달이 우리를 보고 있었어.
			조종사: 계기나 봐. 연료가 안 줄어. 이륙하고 네 시간째인데.
			사수: 헬파이어를 열여섯 발 쐈는데 레일에 열여섯 발이 다 걸려 있어.
			조종사: ...임무 지시 들어왔다. 인증 맞다. 계속한다.
			[System] ROTOR RPM LOW. ROTOR RPM LOW.
			조종사: 메이데이, 원-원 추락한다. 누가 듣고 있으면, 우리는 훈련 중이었다. 우리는
			(기록 끝)
			\'\'\'
	}
	LoreGuardian: {
		DisplayName: "회수 기록: 가디언 편대 데이터링크 로그"
		Tooltip: AH-64E에서 뽑아낸 데이터 전송 카트리지
		LoreText:
			\'\'\'
			[TCDL] AH-64E / MQ-1C / RQ-7B  LINK UP
			[TASKING] 출처 ????  인증 VALID  우선순위 FLASH
			    임무: 식별 불가 대상 1. 무력화.
			[QUERY] 가디언 → 지휘망: 임무 출처 확인 요청
			[REPLY] 출처 ????  인증 VALID  "확인할 필요 없음"
			[NOTE] 섀도 영상 0412: 대상이 격추된 원-원 잔해에서 레이저 지시기를 주웠다. 우리 코드로 우리 아파치를 불렀다.
			[NOTE] 그레이 이글 지상통제 로그인 기록: 소속 칸 공란, 사용자 1명. 우리가 아는 사람이 아니다.
			[NOTE] 반송파 세기가 올라간다. 하늘에서 뭔가 깨질 때마다 한 단계씩.
			[TASKING] 출처 ????  인증 VALID
			    다음 부대 전개. 호출부호 없음. 해상.
			[TCDL] LINK LOST
			\'\'\'
	}
"""

EN = """	LoreHint: "Hold Shift to read the record"
	LoreHumvee: {
		DisplayName: "Recovered Record: Dagger Two-One Patrol Notebook"
		Tooltip: A waterproof notebook from the driver's seat of the burnt-out Humvee
		LoreText:
			\'\'\'
			[D+0 0213Z] NTC night rotation, day 3. Strange carrier on every net. Commo says it sounds like singing.
			[D+0 0214Z] The desert is gone. Forest. Zero GPS satellites. Terrain not on any map.
			[D+0 0300Z] Company net's dead. Nobody answers. Tasking keeps coming in anyway, and the authentication checks out.
			[D+1 0540Z] One unidentified person ahead. No IFF reply. Classified hostile per ROE.
			[D+1 0712Z] Green jelly thing stuck itself to the truck. Gunner put the fifty on it. I should tell the guys this isn't the exercise. I don't know that.
			[D+3 1900Z] Changed belts three times. The ammo can is still full. Nobody talks about it.
			[D+4 ----Z] Hauler Two-Six came up on the net. Asked if they were here to pick us up. They read back the auth code and went off.
			(last page, different handwriting) Dagger Two-One, contact. Target unidentified. Engaging.
			\'\'\'
	}
	LoreApache: {
		DisplayName: "Recovered Record: One-One Cockpit Voice Recording"
		Tooltip: A transcript read off the flight data recorder pulled from the wreck
		LoreText:
			\'\'\'
			(CVR readout. Callsign One-One. Every recorder timestamp reads exercise day, 00:00:00Z)
			CPG: One target on the radar. Interrogating.
			PLT: Reply?
			CPG: Nothing. No Mode 5, no Mode 4.
			PLT: Then it's by the book. One-One, engaging.
			(12 seconds, no audio)
			CPG: Did you see the moon just now? It was looking at us.
			PLT: Watch your instruments. Fuel isn't going down. We've been up four hours.
			CPG: I've fired sixteen Hellfires. All sixteen are still on the rails.
			PLT: ...Tasking's in. Auth's good. Continuing.
			[System] ROTOR RPM LOW. ROTOR RPM LOW.
			PLT: Mayday, One-One going down. If anybody's listening, we were on an exercise. We were
			(end of recording)
			\'\'\'
	}
	LoreGuardian: {
		DisplayName: "Recovered Record: Guardian Flight Data-Link Log"
		Tooltip: The data transfer cartridge pulled out of the AH-64E
		LoreText:
			\'\'\'
			[TCDL] AH-64E / MQ-1C / RQ-7B  LINK UP
			[TASKING] SRC ????  AUTH VALID  PRIORITY FLASH
			    Task: one unidentified target. Neutralize.
			[QUERY] Guardian -> command net: request source of tasking
			[REPLY] SRC ????  AUTH VALID  "Not required"
			[NOTE] Shadow video 0412: target picked a laser designator out of One-One's wreck. Called our Apache with our codes.
			[NOTE] Gray Eagle ground control login: unit field blank, one user. Nobody we know.
			[NOTE] Carrier strength is rising. One step every time something breaks in the sky.
			[TASKING] SRC ????  AUTH VALID
			    Next unit deploying. No callsign. Maritime.
			[TCDL] LINK LOST
			\'\'\'
	}
"""


def main(block, path):
    s = open(path, encoding='utf-8').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    s = s.replace('\r\n', '\n')
    if 'LoreHumvee' in s:
        print('already', path)
        return
    start = s.index('\nItems: {') + 1
    end = s.index('\n}', start)
    s = s[:end] + '\n' + block.rstrip('\n') + s[end:]
    open(path, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
    print('ok', path)


if __name__ == '__main__':
    main(KO, 'ko-KR_Mods.ModernArsenal.hjson')
    main(EN, 'en-US_Mods.ModernArsenal.hjson')
