/*
 * Decompiled with CFR 0.152.
 */
package jnode.workers;

import java.io.File;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import jnode.modelEntities.ClassAnalysis;
import jnode.workers.CRModel;
import jnode.workers.ClassycleWorker;

public class StaticAnalysisWorker {
    private boolean mergeInnerClasses = true;
    private List<ClassAnalysis> classes;
    private String path;
    String initPackage;

    public StaticAnalysisWorker(String pp) {
        this.path = pp;
    }

    public void doItClassycle() {
        File np = new File(this.path);
        File[] cnp = np.listFiles();
        String npath = "";
        if (cnp.length > 0) {
            int i = 0;
            while (i < cnp.length) {
                if (cnp[i].getAbsoluteFile().toString().endsWith(".jar")) {
                    npath = cnp[i].getAbsolutePath();
                    break;
                }
                ++i;
            }
        }
        ClassycleWorker classycleWr = new ClassycleWorker(npath, this.mergeInnerClasses);
        this.classes = new ArrayList<ClassAnalysis>(0);
        this.classes = classycleWr.getClassAnalysis();
    }

    // EPL484 performance patch: index of class name -> position (was a linear scan per call)
    private java.util.Map<String, Integer> placeIndex;

    private int getPlace(String name, List<ClassAnalysis> clcs) {
        if (clcs == this.classes) {
            if (this.placeIndex == null || this.placeIndex.size() != clcs.size()) {
                this.placeIndex = new java.util.HashMap<String, Integer>();
                for (int k = clcs.size() - 1; k >= 0; --k) {
                    this.placeIndex.put(clcs.get(k).getName(), k);
                }
            }
            Integer p = this.placeIndex.get(name);
            return p == null ? -1 : p;
        }
        int i = 0;
        while (i < clcs.size()) {
            if (clcs.get(i).getName().equals(name)) {
                return i;
            }
            ++i;
        }
        return -1;
    }

    public void doItCRModel() {
        CRModel inWr = new CRModel(this.classes);
        inWr.doIt();
        this.classes = new ArrayList<ClassAnalysis>(0);
        this.classes = inWr.getClassAnalysis();
    }

    public void doItClusterDependenciesExtraction() {
        int i = 0;
        while (i < this.classes.size()) {
            Set<String> sub = this.subsystem(this.classes.get(i).getName(), i);
            this.classes.get(i).setClusterClasses(sub);
            ++i;
        }
    }

    public Set<String> subsystem(String forClass, int forClassIndex) {
        HashSet<String> visited = new HashSet<String>();
        Set<String> dependencies = this.subsystem(visited, forClass, forClassIndex);
        return dependencies;
    }

    private Set<String> subsystem(Set<String> visited, String forClass, int forClassIndex) {
        if (visited.contains(forClass)) {
            return visited;
        }
        visited.add(forClass);
        Set<String> neighbors = this.classes.get(forClassIndex).getClassesesForDependency();
        for (String c : neighbors) {
            visited = this.subsystem(visited, c, this.getPlace(c, this.classes));
        }
        return visited;
    }

    public List<ClassAnalysis> getClassesVectorAfterAnalysis() {
        return this.classes;
    }
}

