/*
 * Copyright (c) 2020.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.sbweb.controller.queuedapi;

import com.hagoapp.poc.sbweb.controller.AppInfo;
import com.hagoapp.poc.sbweb.controller.TaskInfo;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;

public class QueueApiController {

    private static class AppListRunner extends ApiRunner<List<AppInfo>> {

        private final String userId;

        public AppListRunner(String uid) {
            userId = uid;
        }

        @Override
        String getQueueIdentity() {
            return userId;
        }

        @Override
        List<AppInfo> getApiResult() {
            return List.of(
                    AppInfo.create("1", "app1"),
                    AppInfo.create("2", "app2")
            );
        }
    }

    @GetMapping
    @ResponseBody
    public List<AppInfo> getAppList(@RequestParam String uid) {
        try {
            var task = new AppListRunner(uid);
            ApiQueue.addTask(task);
            task.join();
            return task.getApiResult();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    private static class AppInfoRunner extends ApiRunner<AppInfo> {

        private final String userId;
        private final String appId;

        public AppInfoRunner(String uid, String appId) {
            userId = uid;
            this.appId = appId;
        }

        @Override
        String getQueueIdentity() {
            return userId;
        }

        @Override
        AppInfo getApiResult() {
            return AppInfo.create(appId, "app" + appId);
        }
    }

    @GetMapping
    @ResponseBody
    public AppInfo getAppInfo(@RequestParam String uid, @RequestParam String appId) {
        try {
            var task = new AppInfoRunner(uid, appId);
            ApiQueue.addTask(task);
            task.join();
            return task.getApiResult();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    private static class TaskInfoRunner extends ApiRunner<TaskInfo> {

        private final String userId;

        public TaskInfoRunner(String uid) {
            userId = uid;
        }

        @Override
        String getQueueIdentity() {
            return userId;
        }

        @Override
        TaskInfo getApiResult() {
            return null;
        }
    }

    @GetMapping
    @ResponseBody
    public TaskInfo getTaskInfo(@RequestParam String uid) {
        try {
            var task = new TaskInfoRunner(uid);
            ApiQueue.addTask(task);
            task.join();
            return task.getApiResult();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
}
