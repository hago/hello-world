/*
 * Copyright (c) 2020.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc.sbweb.controller.queuedapi;

public abstract class ApiRunner<T> extends Thread {
    abstract String getQueueIdentity();
    abstract T getApiResult();
}
