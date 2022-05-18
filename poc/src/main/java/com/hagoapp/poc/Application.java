/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

package com.hagoapp.poc;

import com.hagoapp.poc.command.ThreadedPipePoc;
import picocli.CommandLine;
import picocli.CommandLine.Command;

@Command(name = "A POC Application", subcommands = {ThreadedPipePoc.class})
public class Application {

    public static void main(String[] args) {
        Application app = new Application();
        CommandLine cli = new CommandLine(app);
        cli.setExecutionStrategy(app::executionStrategy).execute(args);
    }

    private int executionStrategy(CommandLine.ParseResult parseResult) {
        return new CommandLine.RunLast().execute(parseResult); // default execution strategy
    }
}
