/*
 * Decompiled with CFR 0.152 from the course's JNode.jar and patched (see README.md).
 * 
 * Could not load the following classes:
 *  org.objectweb.asm.ClassReader
 *  org.objectweb.asm.ClassVisitor
 */
package jnode.workers;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import jnode.DependencyCollector;
import jnode.modelEntities.ClassAnalysis;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;

public class ClassycleWorker {
    private HashMap<String, ClassAnalysis> classHashMap = new HashMap();

    public ClassycleWorker(String jarName, boolean mergeInnerClasses) {
        try {
            String className;
            HashSet<String> classnames = new HashSet<String>();
            JarFile jarFile = new JarFile(jarName);
            Enumeration<JarEntry> entries2 = jarFile.entries();
            while (entries2.hasMoreElements()) {
                JarEntry entry2 = entries2.nextElement();
                if (!entry2.getName().endsWith(".class")) continue;
                ClassAnalysis temp = new ClassAnalysis();
                className = entry2.getName().replace(".class", "").replace('/', '.');
                classnames.add(className);
                temp.setName(className);
                this.classHashMap.put(temp.getName(), temp);
            }
            System.out.println("Found " + classnames.size() + " classes.");
            System.out.println("Analyzing their dependencies ...");
            jarFile.close();
            jarFile = new JarFile(jarName);
            Enumeration<JarEntry> entries = jarFile.entries();
            while (entries.hasMoreElements()) {
                JarEntry entry = entries.nextElement();
                if (!entry.getName().endsWith(".class")) continue;
                try (InputStream is = jarFile.getInputStream(entry);){
                    ClassReader reader = new ClassReader(is);
                    String className2 = entry.getName().replace(".class", "").replace('/', '.');
                    DependencyCollector analyzer = new DependencyCollector(className2, classnames);
                    reader.accept((ClassVisitor)analyzer, 0);
                    Map<String, Map<String, Map<DependencyCollector.DependencyType, Integer>>> dependencies = analyzer.getDependencies();
                    // PATCH (graph fix): DependencyCollector keeps ONE static map for all
                    // classes read so far. The original iterated over every entry of that
                    // map and attached all of them to className2 as out-dependencies, so a
                    // class "inherited" the dependencies of every class read before it
                    // (order-dependent, wrong graph). Only the entry of className2 is used.
                    Map<String, Map<DependencyCollector.DependencyType, Integer>> own = dependencies.get(className2);
                    if (own != null) {
                        for (String toClass : own.keySet()) {
                            if (!classnames.contains(toClass)) continue;
                            this.classHashMap.get(className2).addClassForDependency(toClass);
                            this.classHashMap.get(toClass).addClassForDependendee(className2);
                        }
                    }
                }
                catch (Exception e) {
                    System.err.println("Error processing " + entry.getName());
                    e.printStackTrace();
                }
            }
            jarFile.close();
            System.out.println("Dependency analysis finished.");
        }
        catch (Exception eee) {
            eee.printStackTrace();
        }
    }

    public List<ClassAnalysis> getClassAnalysis() {
        return new ArrayList<ClassAnalysis>(this.classHashMap.values());
    }
}

