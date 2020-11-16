package com.example.examplemod;

import net.minecraftforge.event.ServerChatEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;


public class EventServerChat {
    @SubscribeEvent
    public void onServerChat(ServerChatEvent event) {
        System.out.format("CHAT EVENT| %s: %s\n", event.getUsername(), event.getMessage());
        String message = event.getMessage();
        switch message {
            case "hello console":
                System.out.format("hello player\n");
                break;
            case "follow me":
                System.out.format("follow me case\n");
                WolfCommands.followPlayer();
                break;
            default:
                break;
        }
    }
}