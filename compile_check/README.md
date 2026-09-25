# 컴파일 검사 파일

- `MACheck.csproj`: 클라우드 `/home/claude/cc/`에 두고, 모드 소스 `.cs` 사본을 `src/` 아래에 둔 뒤 `dotnet build --no-incremental`.
- 참조 dll은 `/mnt/user-data/uploads/tModLoader/`에 있어야 해요 (tModLoader 설치 폴더의 `tModLoader.dll`과 `Libraries/`를 device_stage_files로 올림).
- `nuget.config`: 패키지 소스를 비워 둔 것. 프록시가 nuget.org를 막아서 없으면 복원에서 멈춰요.
- `refl/`: tML 리플렉션 도구. `dotnet build -o out` 후 `dotnet out/refl.dll Terraria.ModLoader.ModMount`처럼 타입 이름을 주면 멤버 시그니처가 나와요.
- 정상 결과: 에러 0, 경고 7개(전부 CS0169, 원래 있던 것).
