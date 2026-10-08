/*
 * Decompiled with CFR 0.152 from the course's JNode.jar and patched (see README.md).
 * 
 * Could not load the following classes:
 *  org.objectweb.asm.ClassReader
 *  org.objectweb.asm.ClassVisitor
 *  org.objectweb.asm.FieldVisitor
 *  org.objectweb.asm.MethodVisitor
 *  org.objectweb.asm.Type
 *  org.objectweb.asm.signature.SignatureReader
 *  org.objectweb.asm.signature.SignatureVisitor
 */
package jnode;

import java.io.IOException;
import java.io.InputStream;
import java.util.EnumMap;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.FieldVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Type;
import org.objectweb.asm.signature.SignatureReader;
import org.objectweb.asm.signature.SignatureVisitor;

public class DependencyCollector
extends ClassVisitor {
    private final String className;
    private static final Map<String, Map<String, Map<DependencyType, Integer>>> dependencies = new HashMap<String, Map<String, Map<DependencyType, Integer>>>();
    private Set<String> clasnamesInSystem;

    public DependencyCollector(String className, Set<String> clasnamesInSystem) {
        super(589824);
        this.className = className;
        this.clasnamesInSystem = clasnamesInSystem;
        dependencies.putIfAbsent(className, new HashMap());
    }

    private void recordDependency(String targetClass, DependencyType type) {
        // PATCH (self-dependency fix): the original compared the internal name
        // ("a/b/C") with the dotted class name ("a.b.C") BEFORE converting it, so
        // the test never matched and every class got a dependency on itself.
        if (targetClass == null || (targetClass = targetClass.replace('/', '.')).equals(this.className)) {
            return;
        }
        if (this.clasnamesInSystem.contains(targetClass)) {
            dependencies.get(this.className).computeIfAbsent(targetClass, k -> new EnumMap<DependencyType, Integer>(DependencyType.class)).merge(type, 1, Integer::sum);
        }
    }

    private void processType(Type type, DependencyType depType) {
        if (type == null) {
            return;
        }
        if (type.getSort() == 10) {
            this.recordDependency(type.getClassName(), depType);
        } else if (type.getSort() == 9) {
            this.processType(type.getElementType(), depType);
        }
    }

    public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
        if (superName != null) {
            this.recordDependency(superName, DependencyType.EXTENDS);
        }
        if (interfaces != null) {
            String[] stringArray = interfaces;
            int n = interfaces.length;
            int n2 = 0;
            while (n2 < n) {
                String iface = stringArray[n2];
                this.recordDependency(iface, DependencyType.IMPLEMENTS);
                ++n2;
            }
        }
        if (signature != null) {
            new SignatureReader(signature).accept((SignatureVisitor)new DependencySignatureVisitor(this));
        }
    }

    public FieldVisitor visitField(int access, String name, String descriptor, String signature, Object value) {
        this.processType(Type.getType((String)descriptor), DependencyType.FIELD_REFERENCE);
        if (signature != null) {
            new SignatureReader(signature).accept((SignatureVisitor)new DependencySignatureVisitor(this));
        }
        return super.visitField(access, name, descriptor, signature, value);
    }

    public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
        this.processType(Type.getReturnType((String)descriptor), DependencyType.TYPE_USAGE);
        // (CFR decompilation artefacts in these two loops rewritten as plain loops)
        for (Type arg : Type.getArgumentTypes((String)descriptor)) {
            this.processType(arg, DependencyType.METHOD_PARAMETER);
        }
        if (signature != null) {
            new SignatureReader(signature).accept((SignatureVisitor)new DependencySignatureVisitor(this));
        }
        if (exceptions != null) {
            for (String ex : exceptions) {
                this.recordDependency(ex, DependencyType.EXCEPTION_THROWS);
            }
        }
        return new MethodVisitor(589824){

            public void visitTypeInsn(int opcode, String type) {
                DependencyCollector.this.recordDependency(type, DependencyType.TYPE_USAGE);
                super.visitTypeInsn(opcode, type);
            }

            public void visitFieldInsn(int opcode, String owner, String name, String descriptor) {
                DependencyCollector.this.recordDependency(owner, DependencyType.FIELD_REFERENCE);
                DependencyCollector.this.processType(Type.getType((String)descriptor), DependencyType.TYPE_USAGE);
                super.visitFieldInsn(opcode, owner, name, descriptor);
            }

            public void visitMethodInsn(int opcode, String owner, String name, String descriptor, boolean isInterface) {
                DependencyCollector.this.recordDependency(owner, DependencyType.METHOD_CALL);
                DependencyCollector.this.processType(Type.getReturnType((String)descriptor), DependencyType.TYPE_USAGE);
                Type[] typeArray = Type.getArgumentTypes((String)descriptor);
                int n = typeArray.length;
                int n2 = 0;
                while (n2 < n) {
                    Type arg = typeArray[n2];
                    DependencyCollector.this.processType(arg, DependencyType.METHOD_PARAMETER);
                    ++n2;
                }
                super.visitMethodInsn(opcode, owner, name, descriptor, isInterface);
            }
        };
    }

    public static void analyzeJar(String jarFilePath, Set<String> clasnamesInSystem) throws IOException {
        JarFile jarFile = new JarFile(jarFilePath);
        Enumeration<JarEntry> entries = jarFile.entries();
        while (entries.hasMoreElements()) {
            JarEntry entry = entries.nextElement();
            if (!entry.getName().endsWith(".class")) continue;
            try (InputStream is = jarFile.getInputStream(entry);){
                ClassReader reader = new ClassReader(is);
                String className = entry.getName().replace(".class", "").replace('/', '.');
                DependencyCollector analyzer = new DependencyCollector(className, clasnamesInSystem);
                reader.accept((ClassVisitor)analyzer, 0);
            }
            catch (Exception e) {
                System.err.println("Error processing " + entry.getName());
                e.printStackTrace();
            }
        }
        jarFile.close();
        DependencyCollector.printResults();
    }

    public static void printResults() {
        for (String fromClass : dependencies.keySet()) {
            for (String toClass : dependencies.get(fromClass).keySet()) {
                for (DependencyType type : dependencies.get(fromClass).get(toClass).keySet()) {
                    int count = dependencies.get(fromClass).get(toClass).get((Object)type);
                    System.out.println(fromClass + " -> " + toClass + " : " + count + " times (" + String.valueOf((Object)type) + ")");
                }
            }
        }
    }

    public Map<String, Map<String, Map<DependencyType, Integer>>> getDependencies() {
        return dependencies;
    }

    private static class DependencySignatureVisitor
    extends SignatureVisitor {
        private final DependencyCollector analyzer;

        public DependencySignatureVisitor(DependencyCollector analyzer) {
            super(589824);
            this.analyzer = analyzer;
        }

        public void visitClassType(String name) {
            this.analyzer.recordDependency(name, DependencyType.TYPE_USAGE);
        }
    }

    public static enum DependencyType {
        EXTENDS,
        IMPLEMENTS,
        METHOD_CALL,
        METHOD_PARAMETER,
        FIELD_REFERENCE,
        TYPE_USAGE,
        EXCEPTION_THROWS;

    }
}

