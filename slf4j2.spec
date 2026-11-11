Name:		slf4j2
Version:	2.0.17
Release:	2
Summary:	Simple Logging Facade for Java
Group:		Development/Java
# log4j-over-slf4j and jcl-over-slf4j are Apache-2.0. The rest is MIT.
License:	MIT AND Apache-2.0
URL:		https://www.slf4j.org/
BuildArch:	noarch

Source0:	https://github.com/qos-ch/slf4j/archive/v_%{version}.tar.gz
Source1:	https://www.apache.org/licenses/LICENSE-2.0.txt

BuildRequires:	java-current-devel
BuildRequires:	sysjar

# 2.0.17-1 published mvn(g:a:2.0.17). That name does not satisfy mvn(g:a).
# Keep the old capability so maven-resolver2 still installs.
Provides:	mvn(org.slf4j:slf4j-api:2.0.17) = 2.0.17
Provides:	mvn(org.slf4j:slf4j-simple:2.0.17) = 2.0.17
Provides:	mvn(org.slf4j:slf4j-nop:2.0.17) = 2.0.17

%description
The Simple Logging Facade for Java (SLF4J) is a facade for logging APIs.
This package is the 2.0.17 API plus the simple and NOP bindings.
Gradle 9.9.1 pins the API at 2.0.17.

%package jdk14
Summary:	SLF4J binding for java.util.logging
Group:		Development/Java
Requires:	%{name} = %{EVRD}
Provides:	mvn(org.slf4j:slf4j-jdk14:2.0.17) = 2.0.17

%description jdk14
SLF4J service provider that sends log events to java.util.logging.

%package jdk-platform-logging
Summary:	SLF4J binding for the JDK platform logger
Group:		Development/Java
Requires:	%{name} = %{EVRD}
Provides:	mvn(org.slf4j:slf4j-jdk-platform-logging:2.0.17) = 2.0.17

%description jdk-platform-logging
SLF4J System.LoggerFinder that routes the JDK platform logger to SLF4J.

%package -n jcl-over-%{name}
Summary:	Jakarta Commons Logging implemented over SLF4J
Group:		Development/Java
Requires:	%{name} = %{EVRD}
Provides:	mvn(org.slf4j:jcl-over-slf4j:2.0.17) = 2.0.17

%description -n jcl-over-%{name}
JCL 1.1 API implemented by calls into SLF4J. Gradle 9.9.1 pins 2.0.17.

%package -n jul-to-%{name}
Summary:	java.util.logging to SLF4J bridge
Group:		Development/Java
Requires:	%{name} = %{EVRD}
Provides:	mvn(org.slf4j:jul-to-slf4j:2.0.17) = 2.0.17

%description -n jul-to-%{name}
Handler that sends java.util.logging records into SLF4J.
Gradle 9.9.1 pins 2.0.17.

%package -n log4j-over-%{name}
Summary:	Log4j 1.2 API implemented over SLF4J
Group:		Development/Java
Requires:	%{name} = %{EVRD}
Provides:	mvn(org.slf4j:log4j-over-slf4j:2.0.17) = 2.0.17

%description -n log4j-over-%{name}
Log4j 1.2 API implemented by calls into SLF4J. Gradle 9.9.1 pins 2.0.17.

%package migrator
Summary:	SLF4J source migrator
Group:		Development/Java
Provides:	mvn(org.slf4j:slf4j-migrator:2.0.17) = 2.0.17

%description migrator
Swing tool that rewrites JCL, JUL, and Log4j calls to SLF4J.

%prep
%autosetup -n slf4j-v_%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
install -p -m 0644 %{SOURCE1} LICENSE-2.0.txt

%build
set -eo pipefail

compile_mod() {
	mod="$1"
	rel="$2"
	expect="$3"
	cp="${4:-}"
	find "$mod/src/main/java" -name '*.java' ! -name module-info.java > "$mod.list"
	test "$(wc -l < "$mod.list")" -eq "$expect"
	mkdir -p "classes-$mod"
	if [ -n "$cp" ]; then
		javac --release "$rel" -encoding UTF-8 -Xlint:-options -cp "$cp" -d "classes-$mod" @"$mod.list"
	else
		javac --release "$rel" -encoding UTF-8 -Xlint:-options -d "classes-$mod" @"$mod.list"
	fi
	if [ -d "$mod/src/main/resources" ]; then
		cp -a "$mod/src/main/resources/." "classes-$mod/"
	fi
	jar cf "$mod.jar" -C "classes-$mod" .
}

write_pom() {
	artifact="$1"
	extra="$2"
	cat > "$artifact.pom" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.slf4j</groupId>
  <artifactId>${artifact}</artifactId>
  <version>2.0.17</version>
  <name>${artifact}</name>
  <url>https://www.slf4j.org/</url>
  <licenses>
    <license>
      <name>MIT License</name>
      <url>https://opensource.org/licenses/MIT</url>
    </license>
  </licenses>
${extra}
</project>
EOF
}

dep_api='  <dependencies>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
  </dependencies>'

compile_mod slf4j-api 8 47
compile_mod slf4j-simple 8 5 slf4j-api.jar
compile_mod slf4j-nop 8 1 slf4j-api.jar
compile_mod jcl-over-slf4j 8 8 slf4j-api.jar
compile_mod jul-to-slf4j 8 1 slf4j-api.jar
compile_mod log4j-over-slf4j 8 30 slf4j-api.jar
compile_mod slf4j-jdk14 8 3 slf4j-api.jar
compile_mod slf4j-jdk-platform-logging 9 3 slf4j-api.jar
compile_mod slf4j-migrator 8 22

write_pom slf4j-api ""
write_pom slf4j-simple "$dep_api"
write_pom slf4j-nop "$dep_api"
write_pom jcl-over-slf4j "$dep_api"
write_pom jul-to-slf4j "$dep_api"
write_pom log4j-over-slf4j "$dep_api"
write_pom slf4j-jdk14 "$dep_api"
write_pom slf4j-jdk-platform-logging "$dep_api"
write_pom slf4j-migrator ""

%install
set -eo pipefail
install_one() {
	artifact="$1"
	list="$2"
	sysjar install --buildroot %{buildroot} \
		--artifact "$artifact.pom:$artifact.jar" \
		--file-name "$artifact" \
		--filelist "$list"
}

install_one slf4j-api .mfiles-api
install_one slf4j-simple .mfiles-simple
install_one slf4j-nop .mfiles-nop
install_one jcl-over-slf4j .mfiles-jcl
install_one jul-to-slf4j .mfiles-jul
install_one log4j-over-slf4j .mfiles-log4j
install_one slf4j-jdk14 .mfiles-jdk14
install_one slf4j-jdk-platform-logging .mfiles-platform
install_one slf4j-migrator .mfiles-migrator
awk '!seen[$0]++' .mfiles-api .mfiles-simple .mfiles-nop > .mfiles

# The previous release owned these paths. Flat sysjar names stay, and
# these symlinks keep the old /usr/share/java/slf4j2 layout working.
J=%{buildroot}%{_javadir}
mkdir -p "$J/slf4j2"
link_jar() {
	list="$1"
	stem="$2"
	shift 2
	for name in "$@"; do
		ln -s "../${stem}.jar" "$J/slf4j2/${name}-%{version}.jar"
		echo "%{_javadir}/slf4j2/${name}-%{version}.jar" >> "$list"
	done
}
echo "%%dir %{_javadir}/slf4j2" >> .mfiles
link_jar .mfiles slf4j-api slf4j-api api
link_jar .mfiles slf4j-simple slf4j-simple simple
link_jar .mfiles slf4j-nop slf4j-nop nop
for list in .mfiles-jcl .mfiles-jul .mfiles-log4j .mfiles-jdk14 .mfiles-platform .mfiles-migrator; do
	echo "%%dir %{_javadir}/slf4j2" >> "$list"
done
link_jar .mfiles-jcl jcl-over-slf4j jcl-over-slf4j
link_jar .mfiles-jul jul-to-slf4j jul-to-slf4j
link_jar .mfiles-log4j log4j-over-slf4j log4j-over-slf4j
link_jar .mfiles-jdk14 slf4j-jdk14 slf4j-jdk14 jdk14
link_jar .mfiles-platform slf4j-jdk-platform-logging slf4j-jdk-platform-logging jdk-platform-logging
link_jar .mfiles-migrator slf4j-migrator slf4j-migrator migrator

%check
set -eo pipefail
mkdir -p check
API=%{buildroot}%{_javadir}/slf4j-api.jar
SIMPLE=%{buildroot}%{_javadir}/slf4j-simple.jar
JCL=%{buildroot}%{_javadir}/jcl-over-slf4j.jar
JUL=%{buildroot}%{_javadir}/jul-to-slf4j.jar
LOG4J=%{buildroot}%{_javadir}/log4j-over-slf4j.jar
MIG=%{buildroot}%{_javadir}/slf4j-migrator.jar
for jar in "$API" "$SIMPLE" "$JCL" "$JUL" "$LOG4J" "$MIG"; do
	test -f "$jar"
done
PROPS="-Dorg.slf4j.simpleLogger.logFile=System.out -Dorg.slf4j.simpleLogger.defaultLogLevel=info"

cat > check/Api.java <<'END'
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public class Api {
	public static void main(String[] args) {
		Logger log = LoggerFactory.getLogger("smoke");
		log.info("slf4j2017_ok {}", log.getName());
	}
}
END
cat > check/Jcl.java <<'END'
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
public class Jcl {
	public static void main(String[] args) {
		Log log = LogFactory.getLog("jcl");
		log.info("jclslf4j_ok " + log.getClass().getName());
	}
}
END
cat > check/Jul.java <<'END'
import java.util.logging.Logger;
import org.slf4j.bridge.SLF4JBridgeHandler;
public class Jul {
	public static void main(String[] args) {
		SLF4JBridgeHandler.removeHandlersForRootLogger();
		SLF4JBridgeHandler.install();
		Logger.getLogger("jul").info("julslf4j_ok");
	}
}
END
cat > check/L4.java <<'END'
import org.apache.log4j.Logger;
public class L4 {
	public static void main(String[] args) {
		Logger.getLogger("log4j").info("log4jslf4j_ok");
	}
}
END
cat > check/Mig.java <<'END'
import org.slf4j.migrator.line.JCLRuleSet;
public class Mig {
	public static void main(String[] args) {
		JCLRuleSet rules = new JCLRuleSet();
		System.out.println("migrator_ok " + rules.getClass().getSimpleName());
	}
}
END

javac --release 8 -encoding UTF-8 -cp "$API" -d check check/Api.java
java $PROPS -cp "check:$SIMPLE:$API" Api > check/api.txt
cat check/api.txt
grep -F -q 'slf4j2017_ok' check/api.txt

javac --release 8 -encoding UTF-8 -cp "$JCL:$API" -d check check/Jcl.java
java $PROPS -cp "check:$JCL:$API:$SIMPLE" Jcl > check/jcl.txt
cat check/jcl.txt
grep -F -q 'jclslf4j_ok' check/jcl.txt

javac --release 8 -encoding UTF-8 -cp "$JUL:$API" -d check check/Jul.java
java $PROPS -cp "check:$JUL:$API:$SIMPLE" Jul > check/jul.txt
cat check/jul.txt
grep -F -q 'julslf4j_ok' check/jul.txt

javac --release 8 -encoding UTF-8 -cp "$LOG4J:$API" -d check check/L4.java
java $PROPS -cp "check:$LOG4J:$API:$SIMPLE" L4 > check/l4.txt
cat check/l4.txt
grep -F -q 'log4jslf4j_ok' check/l4.txt

javac --release 8 -encoding UTF-8 -cp "$MIG" -d check check/Mig.java
java -cp "check:$MIG" Mig > check/mig.txt
cat check/mig.txt
grep -F -q 'migrator_ok' check/mig.txt

%files -f .mfiles
%license LICENSE.txt LICENSE-2.0.txt
%doc README.md

%files jdk14 -f .mfiles-jdk14

%files jdk-platform-logging -f .mfiles-platform

%files -n jcl-over-%{name} -f .mfiles-jcl
%license jcl-over-slf4j/LICENSE.txt

%files -n jul-to-%{name} -f .mfiles-jul

%files -n log4j-over-%{name} -f .mfiles-log4j
%license log4j-over-slf4j/LICENSE.txt

%files migrator -f .mfiles-migrator
