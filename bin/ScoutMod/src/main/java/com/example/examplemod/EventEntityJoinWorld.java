package com.example.examplemod;

import net.minecraft.entity.ai.EntityAIBase;
import net.minecraft.entity.ai.EntityAIFollowOwner;
import net.minecraft.entity.ai.EntityAITasks.EntityAITaskEntry;
import net.minecraft.entity.passive.EntityWolf; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/passive/EntityWolf.html)
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraft.world.World; 

import net.minecraft.entity.player.EntityPlayer; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/player/EntityPlayer.html)
// EntityPlayer
import java.util.UUID;

public class EventEntityJoinWorld {
    @SubscribeEvent
    public void onEntityJoinWorld(EntityJoinWorldEvent event) {
        if (event.getEntity() instanceof EntityWolf) {
            World world = event.getWorld();
            EntityWolf pupper = (EntityWolf) event.getEntity();
            
            System.out.format("Player Entities Size: %d\n", world.playerEntities.size());

            if (world.playerEntities.size() == 0) {
                return;
            }
            EntityPlayer player = world.playerEntities.get(0);
            System.out.format("Player Name: %s\n", player.getName());
            UUID user_id = EntityPlayer.getOfflineUUID(player.getName());
            pupper.setOwnerId(user_id); //java.util.UUID
            pupper.setTamed(true);
            
            for (Object a : pupper.tasks.taskEntries.toArray()) {
                EntityAIBase entryAction = ((EntityAITaskEntry) a).action;
                
                if (entryAction instanceof EntityAIFollowOwner) {
                    pupper.tasks.removeTask(entryAction);
                }
            }
        }
    }
}