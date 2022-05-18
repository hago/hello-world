/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.threadedpipe;

public class TaskConfigGenerator {

    public static TaskConfigGenerator CreateGenerator(int taskNumber) {
        return new TaskConfigGenerator(taskNumber);
    }

    private final int taskNum;
    private int generatedNum = 0;

    private TaskConfigGenerator(int num) {
        taskNum = num;
    }

    public synchronized TaskConfig getTask() {
        if (generatedNum < taskNum) {
            generatedNum++;
            var t = new TaskConfig();
            t.setName("Task No." + generatedNum);
            return t;
        } else {
            return null;
        }
    }
}
