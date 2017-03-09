#!/usr/bin/python
# -*- coding: utf-8 -*-
# global section

import StringIO

def generate_tests(sample_groups, online_groups, offline_groups):
    valuercfg = StringIO.StringIO()
    servecfg = StringIO.StringIO()
    err = StringIO.StringIO()
    print >>valuercfg, """global {
    stat_to_judges 1;
    stat_to_users 1;
}
"""

    class GroupPrinter:
        def __init__(self):
            self.group_index = 0
            self.test_index = 1
            self.group_test_indices = []
        def print_group(self, test_count, extra_options):
            first_test = self.test_index
            last_test = self.test_index + test_count - 1
            self.test_index += test_count
            self.group_test_indices.append((first_test, last_test))
            print >>valuercfg, """group {0} {{
    tests {1}-{2};""".format(self.group_index, first_test, last_test)
            self.group_index += 1
            print >>valuercfg, ';\n'.join("    " + option for option in extra_options) + ";"
            print >>valuercfg, "}\n"

    gp = GroupPrinter()

    groups = sample_groups + online_groups + offline_groups 
    online_groups = len(online_groups)
    offline_groups = len(offline_groups)

    test_count = [group[0] for group in groups]
    test_points = [group[1] for group in groups]
    for i in range(0, 1 + online_groups + offline_groups):
        extra_options = []
        if groups[i][2] != "":
            extra_options.append("requires " + groups[i][2])
        extra_options.append("score " + groups[i][1])
        if i == online_groups and offline_groups > 0:
            extra_options.append("sets_marked_if_passed " + ", ".join(map(str, range(i + 1))))
        if i > online_groups:
            extra_options.append("offline")
        try: 
            test_count[i] = int(test_count[i])
        except:
            print >>err, "Wrong test count for group {0}: {1}".format(i, groups[i][0])
            break

        try:
            test_points[i] = int(test_points[i])
        except:
            print >>err, "Wront points for group {0}: {1}".format(i, groups[i][1])
            break

        gp.print_group(test_count[i], extra_options)

    if err.getvalue() == "":
        print >>servecfg, "test_score_list=\"" + '  '.join(' '.join("0" if j + 1 < tc or i == 0 else groups[i][1] for j in range(tc)) for i, tc in enumerate(test_count)) + "\""
        open_tests="{0}-{1}:full".format(*gp.group_test_indices[0])
        if online_groups > 0:
            open_tests += ",{0}-{1}:brief".format(gp.group_test_indices[1][0], gp.group_test_indices[online_groups][1])
        if offline_groups > 0:
            open_tests += ",{0}-{1}:hidden".format(gp.group_test_indices[online_groups + 1][0], gp.group_test_indices[-1][1])
        print >>servecfg, "open_tests=\"{0}\"".format(open_tests)
        print >>servecfg, "full_user_score={0}".format(sum(test_points[:(1 + online_groups)]))
        if sum(test_points) != 100:
            print >>err, "Sum of all group points is {0} != 100".format(sum(test_points))
  
    print >>valuercfg, '\n'.join("# " + line for line in servecfg.getvalue().strip().split("\n"))

    return valuercfg.getvalue(), servecfg.getvalue(), err.getvalue()
